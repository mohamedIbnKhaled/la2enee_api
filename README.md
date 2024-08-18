# Face Recognition Flask Application

## Overview

This project is a Flask-based web application that uses facial recognition technology to match and identify individuals. It integrates with Firebase for data storage and messaging and uses environment variables for configuration. The application has endpoints for uploading images, matching faces, liking and commenting on posts, and editing user profiles.

## Features

- **Face Recognition**: Identifies individuals based on facial features.
- **Firebase Integration**: Uses Firestore for storing face vectors and user data, and Firebase Cloud Messaging for notifications.
- **Image Upload**: Handles image uploads for finding or seeking individuals.
- **Notifications**: Sends notifications when users like or comment on posts.
- **Profile Editing**: Allows users to update their profile information.

## Requirements

- Python 3.x
- Flask
- face_recognition
- firebase_admin
- numpy
- requests
- python-dotenv

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/yourusername/your-repository.git
    cd your-repository
    ```

2. **Create a virtual environment** (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:

    Create a `.env` file in the root directory of the project with the following content:

    ```plaintext
    type=your_type
    project_id=your_project_id
    private_key_id=your_private_key_id
    private_key=your_private_key
    client_email=your_client_email
    client_id=your_client_id
    auth_uri=your_auth_uri
    token_uri=your_token_uri
    auth_provider_x509_cert_url=your_auth_provider_x509_cert_url
    client_x509_cert_url=your_client_x509_cert_url
    ```

5. **Run the application**:

    ```bash
    python app.py
    ```

## API Endpoints

### `POST /finderPost`

Uploads an image and attempts to find a match in the database.

### `POST /seekerPost`

Uploads an image with known identity and attempts to find matching vectors in the database.

**Form Data:**
- `file`: Image file
- `uid`: User ID of the person uploading the image

**Responses:**
- `200 OK`: Match found or vector saved
- `400 Bad Request`: Invalid image or no faces found

### `POST /likes`

Records a like on a post and sends a notification.

### `POST /comment`

Records a comment on a post and sends a notification.

### `POST /edit`

Updates user profile information.

