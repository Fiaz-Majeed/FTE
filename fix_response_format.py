#!/usr/bin/env python3
"""Fix email responses to use the proper format that the auto-reply system expects."""

import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fte.vault_manager import VaultManager

def fix_email_response_format(email_file_path):
    """Fix the response format in an email file to match what the auto-reply system expects."""

    file_path = Path(email_file_path)
    if not file_path.exists():
        return {"success": False, "error": f"Email file not found: {email_file_path}"}

    content = file_path.read_text(encoding='utf-8')

    # Look for our custom response marker
    custom_response_marker = "---\n**Response to Course Assignment Request**"
    custom_response_pos = content.find(custom_response_marker)

    if custom_response_pos != -1:
        # Extract our custom response
        start_pos = content.find("\n", custom_response_pos)
        if start_pos != -1:
            # Find the end of the response (next section or end of content)
            remaining_content = content[start_pos:]
            lines = remaining_content.split('\n')
            response_lines = []
            for line in lines[1:]:  # Skip the first newline
                if line.startswith("---") or line.startswith("#") or line.strip() == "":
                    if line.startswith("---") and len(response_lines) > 0:
                        # Found the separator, stop here
                        break
                    elif line.strip() == "" and len([l for l in response_lines if l.strip()]) > 0:
                        # Empty line after we already have content, continue collecting
                        response_lines.append(line)
                        continue
                    elif not line.startswith("#"):
                        # Empty line or continuation, add to response
                        response_lines.append(line)
                        continue
                    else:
                        # Found a new section
                        break
                else:
                    response_lines.append(line)

            response = '\n'.join(response_lines).strip()

            # Remove the old response section
            new_content = content[:custom_response_pos].rstrip()

            # Add the properly formatted AI response
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            proper_response = f"\n\n---\n**AI Generated Response** - {timestamp}\n{response}\n---\n"

            updated_content = new_content + proper_response

            # Write the updated content back to the file
            file_path.write_text(updated_content, encoding='utf-8')

            return {
                "success": True,
                "message": f"Fixed response format in {file_path.name}",
                "response": response
            }
    else:
        return {
            "success": False,
            "error": "Custom response not found in file"
        }

if __name__ == "__main__":
    # Fix the response format for the course assignment email
    email_file = "vault/Needs_Action/20260129_122657_Request to assign a course.md"

    # If it's not in Needs_Action, check if it's in Done and move it back
    email_path = Path(email_file)
    if not email_path.exists():
        done_file = "vault/Done/20260129_122657_Request to assign a course.md"
        done_path = Path(done_file)
        if done_path.exists():
            # Move from Done back to Needs_Action for testing
            import shutil
            shutil.move(str(done_path), str(email_path))
            print(f"Moved email from Done back to Needs_Action: {email_path.name}")

    result = fix_email_response_format(str(email_path))
    print(result)