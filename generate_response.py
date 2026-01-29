#!/usr/bin/env python3
"""Script to generate an appropriate response for the ceiling lights request."""

import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fte.skills.email_response_generator import generate_email_response

def main():
    # Path to the email file in Needs_Action folder
    email_file_path = "vault/Needs_Action/20260129_105519_Fwd_ Request for Installation of Two New Ceiling L.md"

    print("Generating response for ceiling lights request...")

    # Generate a custom response for the ceiling lights request
    custom_response = f"""
---

**Response to Request for Ceiling Lights Installation**

Dear Iram Shahzadi,

Thank you for your request regarding the installation of two new ceiling lights in Office #216.

I acknowledge that this request was initially submitted verbally in November 2024 and that the lighting issue persists. I apologize for the delay in addressing this matter.

I will coordinate with the facilities management team to schedule the installation of the ceiling lights in Office #216 as soon as possible. We will prioritize this work to ensure adequate lighting for your office space.

I will contact you directly once we have a timeline for the installation.

Best regards,

Dr. Fiaz Majeed
Chairperson, Department of Information Technology
University of Gujrat
"""

    # Read the existing file and append the response
    file_path = Path(email_file_path)
    if file_path.exists():
        content = file_path.read_text(encoding='utf-8')

        # Check if response already exists
        if "**Response to Request for Ceiling Lights Installation**" not in content:
            updated_content = content + custom_response
            file_path.write_text(updated_content, encoding='utf-8')
            print(f"Response added to {file_path.name}")
        else:
            print("Response already exists in the file.")

        # Move the file to Done folder
        done_folder = Path("vault/Done")
        done_folder.mkdir(exist_ok=True)

        done_file_path = done_folder / file_path.name
        file_path.rename(done_file_path)

        print(f"Email moved to Done folder: {done_file_path.name}")
    else:
        print(f"Email file not found: {email_file_path}")

if __name__ == "__main__":
    main()