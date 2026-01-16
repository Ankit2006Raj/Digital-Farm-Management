# 🌾 Smart Farm Management System

A comprehensive AI-powered farm management platform built with Flask that helps farmers manage cattle, fish, poultry, and overall farm operations efficiently. This system integrates AI analytics, health monitoring, marketplace features, and intelligent scheduling to modernize farm management.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

<img width="1355" height="632" alt="image" src="https://github.com/user-attachments/assets/a4f89994-0382-4833-a6a6-6611769d249d" />
<img width="1362" height="618" alt="image" src="https://github.com/user-attachments/assets/b2ad2eb3-08cc-43eb-a300-b76f5bf9fd66" />


## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Modules](#-modules)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

## ✨ Features

### 🐄 Cattle Management
- Track individual cattle with unique tag numbers
- Monitor breed, age, weight, and health status
- Health check and anomaly detection using AI
- Nutrition recommendations based on cattle data
- Lifecycle tracking dashboard
- Vaccination and treatment scheduling

### 🐟 Fish Farming
- Pond-wise fish management
- Water quality monitoring (temperature, pH levels)
- Species tracking and stocking dates
- Production analytics
- Health monitoring and disease detection

### 🐔 Poultry Management
- Coop-based tracking system
- Daily egg production monitoring
- Breed management
- Health records and vaccination tracking
- Feed consumption analysis

### 🤖 AI-Powered Analytics
- Predictive health analysis
- Production forecasting
- Anomaly detection in livestock behavior
- Data-driven insights and recommendations
- Activity log tracking

### 🗓️ Smart Calendar
- Schedule farm activities and tasks
- Vaccination reminders
- Feeding schedules
- Maintenance alerts
- Event tracking and completion status

### 🛒 Marketplace
- Buy and sell farm products
- List equipment and services
- Community trading platform
- Contact management

### 💬 AI Assistant
- Voice-enabled farm assistant
- Natural language queries
- Farm data insights
- Task automation support

## 🛠️ Tech Stack

**Backend:**
- Python 3.8+
- Flask 2.3.3
- SQLAlchemy (Database ORM)
- SQLite (Database)

**AI & Machine Learning:**
- OpenCV (Computer Vision)
- NumPy (Numerical Computing)
- Scikit-learn (Machine Learning)
- Pandas (Data Analysis)
- Matplotlib (Data Visualization)

**Frontend:**
- HTML5
- CSS3
- JavaScript
- Responsive Design

**Additional Libraries:**
- Flask-CORS (Cross-Origin Resource Sharing)
- Pillow (Image Processing)
- python-dateutil (Date Utilities)
- gTTS (Text-to-Speech)
- SpeechRecognition (Voice Input)

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ankit2006Rajand/smart-farm-management.git
cd smart-farm-management
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
The database will be automatically created when you first run the application with sample data.

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🚀 Usage

### Dashboard
Access the main dashboard at the root URL to view:
- Total animal counts across all categories
- Recent health records
- Upcoming scheduled events
- AI analytics insights
- Quick access to all modules

### Managing Livestock
1. Navigate to the respective module (Cattle/Fish/Poultry)
2. Add new animals with detailed information
3. Update health records and treatments
4. View analytics and reports
5. Schedule vaccinations and checkups

### AI Features
- **Health Check**: Upload images for AI-powered health analysis
- **Anomaly Detection**: Identify unusual patterns in livestock behavior
- **Nutrition Recommendations**: Get AI-driven feeding suggestions
- **Production Forecasting**: Predict yields and optimize operations

### Calendar Management
- Create events for farm activities
- Set reminders for important tasks
- Track completion status
- View upcoming schedules

### Marketplace
- List products for sale
- Browse available items
- Connect with other farmers
- Manage transactions

## 📁 Project Structure

```
smart-farm-management/
│
├── app.py                      # Main application file
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── instance/
│   └── farm_management.db      # SQLite database
│
├── modules/                    # Application modules
│   ├── __init__.py
│   ├── cattle.py              # Cattle management
│   ├── fish.py                # Fish farming
│   ├── poultry.py             # Poultry management
│   ├── ai_analytics.py        # AI analysis engine
│   ├── ai_assistant.py        # Voice assistant
│   ├── calendar_module.py     # Event scheduling
│   ├── marketplace.py         # Trading platform
│   └── community.py           # Community features
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css          # Stylesheets
│   ├── js/
│   │   └── main.js            # JavaScript files
│   └── uploads/               # Uploaded images
│       ├── cattle/
│       ├── fish/
│       └── poultry/
│
└── templates/                  # HTML templates
    ├── base.html              # Base template
    ├── dashboard.html         # Main dashboard
    ├── ai/                    # AI module templates
    ├── assistant/             # Assistant templates
    ├── calendar/              # Calendar templates
    ├── cattle/                # Cattle templates
    ├── fish/                  # Fish templates
    ├── poultry/               # Poultry templates
    ├── marketplace/           # Marketplace templates
    └── community/             # Community templates
```

## 🔧 Modules

### Cattle Module
- Individual animal tracking
- Health monitoring
- Weight management
- Breeding records
- AI-powered health checks

### Fish Module
- Pond management
- Water quality tracking
- Species monitoring
- Harvest planning

### Poultry Module
- Coop management
- Egg production tracking
- Feed management
- Health records

### AI Analytics
- Predictive modeling
- Pattern recognition
- Health diagnostics
- Production optimization

### Calendar Module
- Event scheduling
- Task management
- Reminder system
- Activity tracking

### Marketplace
- Product listings
- Service offerings
- Community trading
- Contact management

## 📸 Screenshots

*Add screenshots of your application here to showcase the UI and features*

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add comments for complex logic
- Test your changes thoroughly
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Ankit Raj**

A passionate developer focused on creating innovative solutions for agriculture and farm management. This project aims to bridge the gap between traditional farming and modern technology, making farm management more efficient and data-driven.

### Connect with Me

- 📧 Email: [ankit9905163014@gmail.com](mailto:ankit9905163014@gmail.com)
- 💼 LinkedIn: [Ankit Raj](https://www.linkedin.com/in/ankit-raj-226a36309)
- 🐙 GitHub: [@Ankit2006Rajand](https://github.com/Ankit2006Rajand)

### Support

If you find this project helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🤝 Contributing to the codebase

---

## 🙏 Acknowledgments

- Thanks to the open-source community for the amazing libraries and tools
- Inspired by the need to modernize agricultural practices
- Built with ❤️ for farmers and agricultural professionals

## 📞 Contact & Support

For questions, suggestions, or support:
- Open an issue on GitHub
- Email: ankit9905163014@gmail.com
- Connect on LinkedIn for professional inquiries

---

**Made with 💚 for sustainable farming**

*Last Updated: January 2026*
"# Digital-Farm-Management" 
