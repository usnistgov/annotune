# Annotation and Text Understanding and Navigation Engine (Annotune)

The Annotune is a web-based application built with Flask that allows users to annotate data using an external API. Users can specify the API URL and utilize this app to make annotations conveniently.

## Prerequisites

Before you can run this application on your own, please make sure you have the following software installed on your system:

- Python 3.x installed.
- [Pip](https://pip.pypa.io/en/stable/installing/) installed.
- Git (optional).

## Installation

1. Clone the repository (if you have Git installed) or download the source code.

   ```bash
   git clone https://github.com/daniel-stephens/community_resilience.git
   ```

   OR

   [Download the ZIP file](https://github.com/daniel-stephens/community-resilience/archive/main.zip) and extract it.

2. Navigate to the submodule 2023-document-annotation
    ```bash
    cd 2023-document-annotation
    ```

3. Pull the latest version of the submodule
    ```bash
    git pull
    ```

4. Navigate back and to the project directory:

   ```bash
   cd ..

   cd annotation_app
   ```

5. Install the required packages from `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration
    Refer to the readme  of the  2023-document-annotation to set it up. 
    In the app.py file, paste the url on which this setup is on.

    url = "url from the 2023_document_anotation"
## Running the Application

Follow these steps to run the Annotation App on your own:

1. Make sure you are in the project directory:

   ```bash
   cd annotation-app
   ```

2. Run the Flask application:

   ```bash
   python app.py
   ```

3. Open a web browser and navigate to `http://localhost:5000`.

4. Specify the API URL to connect to your data source.

5. Start making annotations!

## Usage

- Once the application is running, you can access it via a web browser.
- Specify the API URL you want to connect to when prompted.
- Use the app to make annotations based on the data from the API.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.

2. Create a new branch:

   ```bash
   git checkout -b feature/my-feature
   ```

3. Commit your changes:

   ```bash
   git commit -m "Add my feature"
   ```

4. Push to your branch:

   ```bash
   git push origin feature/my-feature
   ```

5. Open a Pull Request on GitHub.



Thank you for using the Annotation App! If you have any questions or encounter any issues, please feel free to open an issue on the [GitHub repository](https://github.com/your-username/annotation-app).
