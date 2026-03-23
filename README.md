# Formix AI

Formix AI is an automated desktop application engineered to programmatically navigate, complete, and submit multi-page Google Forms. Designed primarily to streamline repetitive academic and institutional workflows, the application integrates browser automation with large language models to evaluate and answer complex forms in real-time.

## Technical Stack

* **Frontend Interface:** CustomTkinter (Python)
* **Browser Automation:** Selenium WebDriver (utilizing native Selenium Manager)
* **LLM Integration:** OpenRouter REST API (Requests)
* **Application Packaging:** PyInstaller

## Deployment Options

### Option 1: Standalone Executable (For End Users)

A pre-compiled executable is provided for users who do not have a Python environment configured.

1. Navigate to the **Releases** section of this repository and download `Formix AI.exe`.
2. Execute the application.
   *(Note: Windows Defender or SmartScreen may flag the executable as unrecognized. Select "More Info" and "Run Anyway" to proceed.)*
3. Proceed to the Configuration and Usage Guide below.

### Option 2: Source Code Execution (For Developers)

To run or modify the application directly via Python:

#### System Requirements

* Python 3.10 or higher
* Google Chrome or Microsoft Edge

#### Clone the Repository

```bash
git clone https://github.com/yourusername/formix.git
cd formix
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Run the Application

```bash
python app.py
```

## Configuration and Usage Guide

Initial configuration is required to establish the automation profile and bypass institutional authentication barriers.

### Phase 1: API Configuration (OpenRouter)

1. Register a free account at https://openrouter.ai
2. Navigate to the API Keys section and generate a new key
   *(Typically starts with `sk-or-v1-`)*
3. Launch Formix AI and open the Profile tab
4. Input your OpenRouter API key into the designated field
5. Populate your required institutional details:

   * Email
   * Full Name
   * Roll Number
   * PRN
   * College, etc.
6. Select **Save & Apply Profile**

### Phase 2: Browser Authentication Setup

Restricted forms require an active session token. This step establishes your local profile and only needs to be performed once.

1. Return to the Dashboard tab
2. Select **Setup Browser Login**
3. A controlled browser instance will launch and navigate to the Google Account login page
4. Authenticate manually using your institutional credentials
5. Allow the application to detect the successful login

**Important:**

* Do not manually close the browser window
* The application will securely save your session state and terminate automatically

### Phase 3: Execution

1. Input the target Google Form URL into the Dashboard
2. Configure any optional settings (e.g., Auto-submit)
3. Select **Start Automation**
4. Monitor the live logs as the application:

   * Navigates the form
   * Queries the language model
   * Completes and submits responses

## Compliance and Disclaimer

This software is developed strictly for educational purposes and workflow optimization. Users assume full responsibility for their usage of this tool.

It is essential to ensure that your use of automated completion software complies with:

* Your institution's academic integrity guidelines
* The Terms of Service of the platforms being used
