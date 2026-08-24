# 🤖 AI SQL Query Generator

An AI-powered SQL Query Generator that converts **natural-language questions into SQL queries** using the **Groq API and Llama 3.3 70B**, executes the generated SQL, and generates easy-to-understand business insights.

## 📌 Project Overview

The **AI SQL Query Generator** allows users to interact with a database using natural language instead of manually writing SQL queries.

For example, a user can ask:

> "Show me the top 5 customers by total sales."

The application understands the question, generates the appropriate SQL query using **Groq's Llama 3.3 70B model**, executes the query, and presents the results along with a business insight.

## 🔄 How It Works

```text
User Question
      ↓
Natural Language Input
      ↓
Groq API
      ↓
Llama 3.3 70B
      ↓
SQL Query Generation
      ↓
SQL Execution
      ↓
Query Results
      ↓
AI Insight Generation
      ↓
Business-Friendly Output
```

## ✨ Features

* 🗣️ Ask database questions using natural language
* 🤖 Generate SQL queries using Groq AI
* ⚡ Uses Llama 3.3 70B Versatile
* 🗄️ Execute generated SQL queries
* 📊 Display query results
* 💡 Generate business insights from query results
* 🖥️ Interactive Streamlit interface
* 🔐 Secure API key management using `.env`
* 🐍 Built completely with Python

## 🛠️ Technologies Used

| Technology                  | Purpose                                       |
| --------------------------- | --------------------------------------------- |
| **Python**                  | Core programming language                     |
| **Groq API**                | AI inference                                  |
| **Llama 3.3 70B Versatile** | Natural language → SQL and insight generation |
| **SQL**                     | Database querying                             |
| **Streamlit**               | Web application interface                     |
| **Pandas**                  | Data processing                               |
| **python-dotenv**           | Environment variable management               |
| **Git & GitHub**            | Version control                               |

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

## 🧠 AI Model

This project uses the **Groq API** with:

```text
Model: llama-3.3-70b-versatile
```

The model is used for:

1. Understanding the user's natural-language question
2. Generating SQL queries
3. Analyzing SQL query results
4. Producing concise business insights

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/rahul502mv/Ai-Sql-Query-Generator.git
```

Navigate to the project:

```bash
cd Ai-Sql-Query-Generator
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 🔑 Groq API Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The application reads the API key from the environment variable.

### ⚠️ Security

**Never upload your real API key to GitHub.**

Your `.gitignore` should contain:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

For other developers, provide:

```text
.env.example
```

with:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## ▶️ Running the Application

After activating the virtual environment and installing the dependencies:

```powershell
streamlit run app.py
```

If your Streamlit application is inside the `src` directory:

```powershell
streamlit run src/app.py
```

The application will open in your browser.

## 💡 Example

### User Question

```text
Show me the top 5 customers by total sales.
```

### AI Generated SQL

```sql
SELECT
    customer_name,
    SUM(sales) AS total_sales
FROM sales
GROUP BY customer_name
ORDER BY total_sales DESC
LIMIT 5;
```

### Query Result

The generated SQL is executed against the database and the results are displayed in the application.

### AI Business Insight

The application then uses Groq AI to transform the result into a simple business insight that can be understood by a non-technical user.

## 🏗️ Core Components

### 1. SQL Generator

The SQL generator receives:

* User question
* Database schema
* Relevant table information

It sends the information to the **Groq Llama model** and generates the SQL query.

### 2. SQL Execution

The generated SQL query is executed against the connected database.

The results are returned as structured data.

### 3. Insight Generator

The query results are sent back to the Groq model.

The AI analyzes the numbers and produces a short, decision-useful business insight.

## 🎯 Use Cases

This project can be useful for:

* 📊 Data Analysts
* 💼 Business Analysts
* 🧑‍💻 SQL Beginners
* 📈 Business Intelligence
* 🗄️ Database Exploration
* 🤖 Generative AI Applications
* 📋 Automated Business Reporting

## 📚 Learning Objectives

This project demonstrates practical knowledge of:

* Generative AI
* Large Language Models
* Groq API
* Llama models
* Prompt Engineering
* Natural Language to SQL
* Python
* SQL
* Database Integration
* Streamlit
* Pandas
* Environment Variables
* Git & GitHub

## 🔮 Future Improvements

* [ ] PostgreSQL support
* [ ] MySQL support
* [ ] Multiple database support
* [ ] SQL query validation
* [ ] Query history
* [ ] Data visualization
* [ ] Automatic chart generation
* [ ] Conversational database querying
* [ ] Database schema auto-detection
* [ ] User authentication
* [ ] Cloud deployment
* [ ] Improved SQL security

## 🔐 API Key Security

Never commit your API key.

❌ Do not upload:

```text
.env
```

✅ Upload:

```text
.env.example
```

Example:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## 👨‍💻 Author

**RAHUL M**

GitHub: [@rahul502mv](https://github.com/rahul502mv)

### 🚀 Built With

**Python • Groq API • Llama 3.3 70B • SQL • Streamlit • Pandas**
