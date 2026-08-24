# AI SQL Query Generator

An AI-powered SQL Query Generator that converts natural-language questions into SQL queries using the OpenAI API, executes the generated SQL, and provides easy-to-understand business insights.

## 🚀 Project Overview

The **AI SQL Query Generator** allows users to interact with a database using natural language instead of writing SQL manually.

For example:

> "Show me the top 5 customers by total sales."

The application uses an AI model to understand the question and generate the appropriate SQL query.

### Workflow

```text
User Question
      ↓
Natural Language Processing
      ↓
OpenAI API
      ↓
SQL Query Generation
      ↓
SQL Validation / Execution
      ↓
Database Results
      ↓
AI Business Insight
      ↓
Streamlit Dashboard
```

## ✨ Features

* Convert natural-language questions into SQL
* Generate SQL using OpenAI
* Execute generated SQL against the database
* Display SQL query and query results
* Generate business-friendly insights from query results
* Interactive Streamlit interface
* Environment-variable based API key configuration
* Easy local setup and deployment

## 🛠️ Technologies Used

* **Python**
* **OpenAI API**
* **Streamlit**
* **Pandas**
* **SQLite / SQL Database**
* **python-dotenv**
* **Git & GitHub**

## 📁 Project Structure

```text
Ai-Sql-Query-Generator/
│
├── src/
│   ├── sql_generator.py
│   ├── insights_generator.py
│   └── ...
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── ...
```

> The exact files may vary depending on the current project implementation.

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/rahul502mv/Ai-Sql-Query-Generator.git
```

Move into the project directory:

```bash
cd Ai-Sql-Query-Generator
```

If the application is inside a subdirectory, move into that directory as required.

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 🔑 OpenAI API Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

You can use `.env.example` as a template.

### Important

**Never commit your real API key to GitHub.**

The `.gitignore` file should contain:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

## ▶️ Running the Application

Start the Streamlit application with:

```powershell
streamlit run app.py
```

If your Streamlit entry file is located somewhere else, use its correct path, for example:

```powershell
streamlit run src/app.py
```

The application will open in your browser.

## 💡 Example

### User Question

```text
Show me the top 5 customers by total sales.
```

### Generated SQL

```sql
SELECT
    customer_name,
    SUM(sales) AS total_sales
FROM sales
GROUP BY customer_name
ORDER BY total_sales DESC
LIMIT 5;
```

### Result

The application executes the generated SQL and displays the results in the Streamlit interface.

The AI can then convert the results into a business-friendly insight such as:

```text
The top five customers contribute a significant portion of total sales,
with the highest-value customer generating the most revenue.
```

## 🔐 Security

API keys and other sensitive configuration values should be stored in environment variables.

Do not upload:

```text
.env
```

to GitHub.

Use:

```text
.env.example
```

for demonstrating the required environment variables.

## 🎯 Use Cases

This project can be useful for:

* Business analysts
* Data analysts
* SQL beginners
* Business intelligence applications
* Natural-language database interfaces
* Automated reporting
* Data exploration

## 🔮 Future Improvements

Possible future improvements include:

* Support for PostgreSQL and MySQL
* SQL query validation
* Automatic database schema detection
* Query history
* Data visualization
* Automatic chart generation
* Multiple AI model support
* User authentication
* Deployment to Streamlit Cloud
* Conversational database querying
* Improved SQL safety and query restrictions

## 📌 Learning Objectives

This project demonstrates practical experience with:

* Generative AI
* Large Language Models
* OpenAI API integration
* Prompt engineering
* Natural-language-to-SQL systems
* Python
* SQL
* Database interaction
* Streamlit
* Environment variables
* Git and GitHub

## 👨‍💻 Author

**RAHUL M**

GitHub: [@rahul502mv](https://github.com/rahul502mv)

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

**Built with Python, SQL, Streamlit, and OpenAI.**
