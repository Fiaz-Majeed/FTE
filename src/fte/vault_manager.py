"""Vault Manager - Read, write, and organize markdown files in the vault."""

from pathlib import Path
from datetime import datetime
import re
import shutil


class VaultManager:
    """Manages the Obsidian vault structure and files."""

    def __init__(self, vault_path: str | Path | None = None):
        """Initialize the vault manager.

        Args:
            vault_path: Path to the vault directory. Defaults to ./vault
        """
        if vault_path is None:
            vault_path = Path(__file__).parent.parent.parent / "vault"
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.done_path = self.vault_path / "Done"
        self.dashboard_path = self.vault_path / "Dashboard.md"

    def ensure_structure(self) -> None:
        """Ensure all required directories exist."""
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)

    def read_file(self, file_path: str | Path) -> str:
        """Read a markdown file from the vault.

        Args:
            file_path: Path to the file (absolute or relative to vault)

        Returns:
            File contents as string
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.vault_path / path
        return path.read_text(encoding="utf-8")

    def write_file(self, file_path: str | Path, content: str) -> Path:
        """Write content to a markdown file.

        Args:
            file_path: Path to the file (absolute or relative to vault)
            content: Content to write

        Returns:
            Path to the written file
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.vault_path / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def list_files(self, folder: str) -> list[Path]:
        """List all markdown files in a folder.

        Args:
            folder: Folder name (Inbox, Needs_Action, Done)

        Returns:
            List of file paths
        """
        folder_path = self.vault_path / folder
        if not folder_path.exists():
            return []
        return [f for f in folder_path.iterdir() if f.suffix == ".md"]

    def move_file(self, file_path: str | Path, destination_folder: str) -> Path:
        """Move a file to a different folder.

        Args:
            file_path: Path to the file to move
            destination_folder: Target folder name (Inbox, Needs_Action, Done)

        Returns:
            New path of the moved file
        """
        source = Path(file_path)
        if not source.is_absolute():
            source = self.vault_path / source

        dest_folder = self.vault_path / destination_folder
        dest_folder.mkdir(parents=True, exist_ok=True)
        dest_path = dest_folder / source.name

        shutil.move(str(source), str(dest_path))
        return dest_path

    def count_files(self, folder: str) -> int:
        """Count markdown files in a folder.

        Args:
            folder: Folder name

        Returns:
            Number of markdown files
        """
        return len(self.list_files(folder))

    def get_status(self) -> dict:
        """Get current vault status.

        Returns:
            Dictionary with counts for each folder
        """
        return {
            "inbox": self.count_files("Inbox"),
            "needs_action": self.count_files("Needs_Action"),
            "done": self.count_files("Done"),
        }

    def update_dashboard(self) -> None:
        """Update the Dashboard.md with current statistics."""
        if not self.dashboard_path.exists():
            return

        content = self.dashboard_path.read_text(encoding="utf-8")
        status = self.get_status()

        # Update Inbox count
        content = re.sub(
            r"\*\*Inbox:\*\* \d+ items",
            f"**Inbox:** {status['inbox']} items",
            content,
        )

        # Update Needs Action count
        content = re.sub(
            r"\*\*Needs Action:\*\* \d+ items",
            f"**Needs Action:** {status['needs_action']} items",
            content,
        )

        # Update last updated timestamp
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        content = re.sub(
            r"_Last updated: .*_",
            f"_Last updated: {today}_",
            content,
        )

        self.dashboard_path.write_text(content, encoding="utf-8")

    def create_note(
        self,
        title: str,
        content: str,
        folder: str = "Inbox",
        tags: list[str] | None = None,
    ) -> Path:
        """Create a new note with frontmatter.

        Args:
            title: Note title (used for filename)
            content: Note body content
            folder: Target folder (default: Inbox)
            tags: Optional list of tags

        Returns:
            Path to the created note
        """
        # Sanitize title for filename
        safe_title = re.sub(r'[<>:"/\\|?*]', "", title)
        safe_title = safe_title.strip()[:100]

        # Build frontmatter
        frontmatter_lines = [
            "---",
            f"title: {title}",
            f"created: {datetime.now().isoformat()}",
        ]
        if tags:
            frontmatter_lines.append(f"tags: [{', '.join(tags)}]")
        frontmatter_lines.append("---")
        frontmatter_lines.append("")

        full_content = "\n".join(frontmatter_lines) + f"# {title}\n\n{content}"

        file_path = self.vault_path / folder / f"{safe_title}.md"
        return self.write_file(file_path, full_content)

    def get_inbox_items(self) -> list[dict]:
        """Get all items in the Inbox with metadata.

        Returns:
            List of dicts with file info and content preview
        """
        items = []
        for file_path in self.list_files("Inbox"):
            content = file_path.read_text(encoding="utf-8")
            # Get first 200 chars as preview (skip frontmatter)
            preview = content
            if content.startswith("---"):
                end_fm = content.find("---", 3)
                if end_fm != -1:
                    preview = content[end_fm + 3 :].strip()
            preview = preview[:200] + "..." if len(preview) > 200 else preview

            items.append(
                {
                    "path": file_path,
                    "name": file_path.stem,
                    "preview": preview,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                }
            )
        return items
