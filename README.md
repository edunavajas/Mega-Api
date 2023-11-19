# Python MEGA API Wrapper

## Overview

This Python API provides a seamless interface with MEGA, offering functionalities to upload, download, delete, and list files stored on MEGA, with a special focus on multimedia content such as photos and videos. It's tailored to handle media files efficiently, making it ideal for personal media management or integration into larger media-focused applications.

## Library Utilization

Due to the discontinuation of the original `mega.py` library, I've incorporated it locally and made necessary modifications to ensure continued functionality. The adapted library can be found at [mega.py on PyPI](https://pypi.org/project/mega.py/).

## Vercel Deployment

The codebase is prepared for deployment on Vercel with the included `vercel.json` file. Deploying a Python function on Vercel is straightforward:

1. Ensure you have the [Vercel CLI](https://vercel.com/download) installed and configured.
2. Clone this repository and navigate to the project directory.
3. Run `vercel` to deploy the project.
4. Follow the prompts to link your project to a Vercel account and deploy your API.

## Environment Variables

Before deployment, ensure that the environment variables are set up correctly. These are critical for the API's operation and include your MEGA account's email and password. The necessary environment variables are:

- `EMAIL`: Your MEGA account email.
- `PASS`: Your MEGA account password.
- `JWT_SECRET_KEY`: A secret key for JWT token generation.
- `JWT_USERNAME`: The username for API authentication.
- `JWT_PASSWORD`: The password for API authentication.
- `UPLOAD_FOLDER`: The local folder for temporarily storing files during upload/download operations.

Remember to replace these with your actual credentials and preferred configuration.

## Authentication

All methods require authentication. The API utilizes JWT for secure access. The user credentials are defined in the environment variables, enabling a database-less authentication mechanism for quick and straightforward setup.

## Endpoints

- `/list`: Lists all files in the linked MEGA account.
- `/upload`: Uploads a file to the MEGA account.
- `/download/<file_key>`: Downloads a file based on its MEGA key.
- `/delete/<file_key>`: Deletes a file based on its MEGA key.
- `/details`: Retrieves details of the linked MEGA account.

Future implementations may include `/download` and `/delete` by URL. While file name-based operations are possible, they are currently not supported due to potential issues with duplicate names and ASCII character encoding.

## Installation

Before running the API, install the required dependencies with the following command:

```bash
pip install -r requirements.txt
