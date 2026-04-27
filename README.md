# Project-MCP  
A lightweight **Multi-Tool MCP Server** built with Python for **Claude Desktop / MCP-compatible clients**. This project combines GitHub tools, file system automation, and PostgreSQL expense tracking into one practical productivity server.

---

# 🚀 Features

## GitHub Tools 🐙
- Repository Details: Fetch repo info, README, and commit insights  
- Repository Search: Search GitHub repositories quickly  

---

## File System Management 📁
- Dynamic Base Directory setup  
- Create Files & Folders  
- Read / Edit / Append Files  
- Rename / Delete Files  
- Search by Filename  
- Search by File Content  
- Restricted system path security  

---

## Expense Tracker 💰
- Automatic PostgreSQL setup  
- Auto database + table creation  
- Add Expenses  
- View All Expenses  
- Search by Category  
- Monthly Summary  
- Highest Expense  
- Delete Expense  

---

# 🔒 Security
- Restricted Windows system folder blocking  
- Base-directory sandboxing for safer file operations  
- PostgreSQL local authentication  
- Environment variable support for sensitive credentials  

---

# 🛠️ Tech Stack

**Backend:** Python, MCP SDK  
**Database:** PostgreSQL  
**API / Requests:** HTTPX  
**Package Manager:** uv  
**Client:** Claude Desktop  

---

# ⚙️ Installation & Setup

## Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/Project-MCP.git
cd Project-MCP
```

---

## Install Dependencies
```bash
Preferable method -  pip install uv 
uv add mcp httpx psycopg2-binary pandas openpyxl
```

Or:

```bash
pip install mcp httpx psycopg2-binary pandas openpyxl
```

---

# 🐘 PostgreSQL Setup

Install **PostgreSQL + pgAdmin 4**

During installation keep:

```text
Username: postgres
Port: 5432
```

Remember your PostgreSQL password.

---

# 🤖 Claude Desktop MCP Setup

Locate Claude config:

```text
%APPDATA%\Claude\claude_desktop_config.json
```

Example Config:

In Claude Under Settings -> Developer -> Edit Config Just paste this Example Config 


```json
{
  "mcpServers": {
    "MCP_Server": {
      "command": "YourDriveName:\\Users\\UserName\\.local\\bin\\uv.exe",
      "args": [
        "run",
        "YourDriveName:\\FolderName\\Mcp_Server.py"
      ]
    }
  },
  "preferences": {
    "menuBarEnabled": false,
    "legacyQuickEntryEnabled": false,
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": false,
    "coworkWebSearchEnabled": true
  }
}
```

---

# 🗄️ Database Setup

Run:

```text
Setup PostgreSQL
```

Note: The server will automatically create:
- `mcp_server` database  
- `expenses` table  

---

# 📂 Project Structure

```text
Project-MCP/
├── Mcp_Server.py
├── README.md
├── requirements.txt
├── .gitignore
└── .env
```

---

# 🌍 Environment Variables

Create a `.env` file:

```env
POSTGRES_PASSWORD=your_password_here
```

---

# 📝 Usage

## File System

### Set Base Directory
```text
Set file system base directory to E:/MCP_Test
```

### Create File
```text
Create file test.txt with content: Hello World
```

### Read File
```text
Read file test.txt
```

---

## Expense Tracker

### Add Expense
```text
Add expense:
Amount: 500
Category: Food
Description: Lunch
```

### View Expenses
```text
View all expenses
```

### Monthly Summary
```text
Show monthly expense summary
```

---

## GitHub Tools

### Repository Details
```text
Get GitHub repo owner=facebook repo=react
```

### Repository Search
```text
Search GitHub repos for MCP Python
```

---

# 🚨 Common Issues

## Module Error
```bash
uv add mcp httpx psycopg2-binary
```

---

## Git Branch Push Error
```bash
git checkout -b Database-Integration
git add .
git commit -m "Added PostgreSQL integration"
git push -u origin Database-Integration
```

---

## Base Directory Restriction
```text
Set file system base directory to E:/MCP_Test
```

---

# 🧪 Testing Checklist

## File System
- Set base dir  
- Create file  
- Edit file  
- Search file  
- Delete file  

## PostgreSQL
- Setup PostgreSQL  
- Add expense  
- View expense  
- Monthly summary  
- Delete expense  

## GitHub
- Repo fetch  
- Repo search  

---

# 🧠 Future Improvements
- CSV export  
- Budget alerts  
- Notes manager  
- Email automation  
- File copy/move tools  
- Analytics dashboard  

---

# 🏁 Final Use Cases

This project is suitable for:

- GitHub Portfolio  
- College Demonstration  
- MCP Learning  
- Python Backend Practice  
- PostgreSQL Practice  
- Automation Tooling  

---

# 📜 License
MIT License (recommended)

---

# 🙌 Author
**Krish Patel / Project-MCP**

