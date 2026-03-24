"""
Odoo MCP Server - JSON-RPC Integration for Accounting System
Provides MCP server for Odoo Community Edition (v19+)
"""
import json
import xmlrpc.client
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

from ..audit.audit_logger import get_audit_logger, AuditEventType
from ..resilience.error_recovery import with_retry, get_circuit_breaker


class OdooClient:
    """Odoo JSON-RPC client for accounting operations."""

    def __init__(
        self,
        url: str = "http://localhost:8069",
        db: str = "odoo",
        username: str = "admin",
        password: str = "admin"
    ):
        """Initialize Odoo client.

        Args:
            url: Odoo server URL
            db: Database name
            username: Odoo username
            password: Odoo password
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None

        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

        self.audit_logger = get_audit_logger()
        self.circuit_breaker = get_circuit_breaker("odoo_api")

    @with_retry(max_attempts=3, initial_delay=2.0)
    def authenticate(self) -> int:
        """Authenticate with Odoo server.

        Returns:
            User ID
        """
        try:
            self.uid = self.circuit_breaker.call(
                self.common.authenticate,
                self.db,
                self.username,
                self.password,
                {}
            )

            if not self.uid:
                raise Exception("Authentication failed")

            self.audit_logger.log_action(
                action="odoo_authenticate",
                actor=self.username,
                resource="odoo",
                status="success"
            )

            return self.uid

        except Exception as e:
            self.audit_logger.log_error(
                f"Odoo authentication failed: {e}",
                actor=self.username,
                resource="odoo"
            )
            raise

    def _execute(self, model: str, method: str, *args, **kwargs) -> Any:
        """Execute Odoo model method.

        Args:
            model: Odoo model name
            method: Method to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Method result
        """
        if not self.uid:
            self.authenticate()

        return self.models.execute_kw(
            self.db,
            self.uid,
            self.password,
            model,
            method,
            args,
            kwargs
        )

    @with_retry(max_attempts=3, initial_delay=2.0)
    def create_invoice(
        self,
        partner_id: int,
        invoice_lines: List[Dict[str, Any]],
        invoice_type: str = "out_invoice"
    ) -> int:
        """Create an invoice.

        Args:
            partner_id: Customer/Vendor ID
            invoice_lines: List of invoice line items
            invoice_type: Invoice type (out_invoice, in_invoice, out_refund, in_refund)

        Returns:
            Invoice ID
        """
        try:
            invoice_data = {
                'partner_id': partner_id,
                'move_type': invoice_type,
                'invoice_line_ids': [(0, 0, line) for line in invoice_lines]
            }

            invoice_id = self.circuit_breaker.call(
                self._execute,
                'account.move',
                'create',
                [invoice_data]
            )

            total = sum(line.get('price_unit', 0) * line.get('quantity', 1) for line in invoice_lines)

            self.audit_logger.log_accounting(
                operation="create_invoice",
                actor=self.username,
                amount=total,
                account=f"invoice_{invoice_id}",
                invoice_type=invoice_type,
                partner_id=partner_id
            )

            return invoice_id

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to create invoice: {e}",
                actor=self.username,
                resource="account.move"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def create_payment(
        self,
        amount: float,
        partner_id: int,
        payment_type: str = "inbound",
        journal_id: Optional[int] = None
    ) -> int:
        """Create a payment.

        Args:
            amount: Payment amount
            partner_id: Customer/Vendor ID
            payment_type: Payment type (inbound, outbound)
            journal_id: Journal ID (optional)

        Returns:
            Payment ID
        """
        try:
            payment_data = {
                'amount': amount,
                'partner_id': partner_id,
                'payment_type': payment_type,
                'partner_type': 'customer' if payment_type == 'inbound' else 'supplier'
            }

            if journal_id:
                payment_data['journal_id'] = journal_id

            payment_id = self.circuit_breaker.call(
                self._execute,
                'account.payment',
                'create',
                [payment_data]
            )

            self.audit_logger.log_accounting(
                operation="create_payment",
                actor=self.username,
                amount=amount,
                account=f"payment_{payment_id}",
                payment_type=payment_type,
                partner_id=partner_id
            )

            return payment_id

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to create payment: {e}",
                actor=self.username,
                resource="account.payment"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def get_account_balance(self, account_id: int) -> float:
        """Get account balance.

        Args:
            account_id: Account ID

        Returns:
            Account balance
        """
        try:
            account = self.circuit_breaker.call(
                self._execute,
                'account.account',
                'read',
                [account_id],
                {'fields': ['balance']}
            )

            if not account:
                raise Exception(f"Account {account_id} not found")

            return account[0]['balance']

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to get account balance: {e}",
                actor=self.username,
                resource=f"account_{account_id}"
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def get_financial_report(
        self,
        report_type: str = "profit_loss",
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get financial report.

        Args:
            report_type: Report type (profit_loss, balance_sheet, cash_flow)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)

        Returns:
            Report data
        """
        try:
            # Get report data based on type
            if report_type == "profit_loss":
                model = "account.financial.html.report"
                report_name = "Profit and Loss"
            elif report_type == "balance_sheet":
                model = "account.financial.html.report"
                report_name = "Balance Sheet"
            else:
                raise ValueError(f"Unknown report type: {report_type}")

            # Search for report
            report_ids = self.circuit_breaker.call(
                self._execute,
                model,
                'search',
                [[('name', '=', report_name)]],
                {'limit': 1}
            )

            if not report_ids:
                raise Exception(f"Report {report_name} not found")

            # Get report lines
            options = {}
            if date_from:
                options['date_from'] = date_from
            if date_to:
                options['date_to'] = date_to

            report_data = self.circuit_breaker.call(
                self._execute,
                model,
                'get_html',
                [report_ids[0]],
                {'options': options}
            )

            self.audit_logger.log_action(
                action="get_financial_report",
                actor=self.username,
                resource=report_type,
                status="success",
                date_from=date_from,
                date_to=date_to
            )

            return {
                "report_type": report_type,
                "date_from": date_from,
                "date_to": date_to,
                "data": report_data,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to get financial report: {e}",
                actor=self.username,
                resource=report_type
            )
            raise

    @with_retry(max_attempts=3, initial_delay=2.0)
    def create_journal_entry(
        self,
        journal_id: int,
        line_ids: List[Dict[str, Any]],
        ref: Optional[str] = None
    ) -> int:
        """Create a journal entry.

        Args:
            journal_id: Journal ID
            line_ids: List of journal line items
            ref: Reference

        Returns:
            Journal entry ID
        """
        try:
            entry_data = {
                'journal_id': journal_id,
                'line_ids': [(0, 0, line) for line in line_ids]
            }

            if ref:
                entry_data['ref'] = ref

            entry_id = self.circuit_breaker.call(
                self._execute,
                'account.move',
                'create',
                [entry_data]
            )

            self.audit_logger.log_accounting(
                operation="create_journal_entry",
                actor=self.username,
                account=f"journal_entry_{entry_id}",
                journal_id=journal_id,
                ref=ref
            )

            return entry_id

        except Exception as e:
            self.audit_logger.log_error(
                f"Failed to create journal entry: {e}",
                actor=self.username,
                resource="account.move"
            )
            raise


# Pydantic models for API
class InvoiceLineItem(BaseModel):
    product_id: int
    quantity: float
    price_unit: float
    name: Optional[str] = None


class CreateInvoiceRequest(BaseModel):
    partner_id: int
    invoice_lines: List[InvoiceLineItem]
    invoice_type: str = "out_invoice"


class CreatePaymentRequest(BaseModel):
    amount: float
    partner_id: int
    payment_type: str = "inbound"
    journal_id: Optional[int] = None


class FinancialReportRequest(BaseModel):
    report_type: str = "profit_loss"
    date_from: Optional[str] = None
    date_to: Optional[str] = None


# FastAPI MCP Server
app = FastAPI(title="Odoo MCP Server", version="1.0.0")

# Global Odoo client
odoo_client: Optional[OdooClient] = None


def get_odoo_client() -> OdooClient:
    """Get or create Odoo client."""
    global odoo_client
    if odoo_client is None:
        odoo_client = OdooClient()
        odoo_client.authenticate()
    return odoo_client


@app.post("/accounting/invoice")
async def create_invoice(request: CreateInvoiceRequest, api_key: str = Header(None)):
    """Create an invoice in Odoo."""
    try:
        client = get_odoo_client()
        invoice_lines = [line.dict() for line in request.invoice_lines]
        invoice_id = client.create_invoice(
            request.partner_id,
            invoice_lines,
            request.invoice_type
        )
        return {"invoice_id": invoice_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/accounting/payment")
async def create_payment(request: CreatePaymentRequest, api_key: str = Header(None)):
    """Create a payment in Odoo."""
    try:
        client = get_odoo_client()
        payment_id = client.create_payment(
            request.amount,
            request.partner_id,
            request.payment_type,
            request.journal_id
        )
        return {"payment_id": payment_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/accounting/report")
async def get_financial_report(request: FinancialReportRequest, api_key: str = Header(None)):
    """Get financial report from Odoo."""
    try:
        client = get_odoo_client()
        report = client.get_financial_report(
            request.report_type,
            request.date_from,
            request.date_to
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounting/balance/{account_id}")
async def get_account_balance(account_id: int, api_key: str = Header(None)):
    """Get account balance from Odoo."""
    try:
        client = get_odoo_client()
        balance = client.get_account_balance(account_id)
        return {"account_id": account_id, "balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        client = get_odoo_client()
        return {"status": "healthy", "odoo_connected": client.uid is not None}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
