# Petroraq ERP Customizations (Odoo 17)

This repository contains a comprehensive set of custom modules and enhancements built on top of Odoo 17 for Petroraq business requirements.

The project extends the standard Odoo ERP system with industry-specific customizations across HR, Accounting, Payroll, Attendance, Purchase, Reporting, and System Enhancements.

All modules are designed with a modular and upgrade-safe approach, ensuring that core Odoo functionality remains untouched while business logic is implemented in separate, maintainable components.

---

## Project Scope

This ERP implementation includes development and customization across multiple business domains:

### HR & Employee Management
- Employee management workflows
- Attendance tracking (ZK integration)
- Leave management system
- Payroll processing
- HR dashboards and reporting
- Organizational structure enhancements

### Accounting & Finance
- Custom ledger enhancements
- Invoice reporting (PDF & Excel)
- Journal sequence customization
- Financial reporting improvements

### Purchase & Inventory
- Purchase request workflow
- Purchase module enhancements
- Inventory update automation (test utilities included)

### Reporting & Analytics
- Dynamic financial reports
- Spreadsheet dashboards
- XLSX-based payroll reports
- Custom analytical views

### System Enhancements
- Web client improvements (list view, notifications, UI tweaks)
- Custom favicon & branding
- Chatter position customization
- Column width enhancements
- Performance and usability improvements

---

## Project Structure

```text
accounting/
HR modules/
purchase/
reporting/
customizations/
core extensions/
utility scripts/
```

> The repository contains multiple independent Odoo modules, each responsible for a specific business function. This ensures scalability and easier maintenance.

---

## Key Modules

Some of the important modules included in this project:

- HR Workspace & Payroll Suite
- Attendance & Time Tracking (ZK Integration)
- Leave Management Dashboard
- Dynamic Financial Reporting Engine
- Purchase Request System
- Custom Accounting Enhancements
- XLSX Payroll Reports
- Spreadsheet Dashboard Tools
- Web Client Enhancements
- System UI Customizations

---

## Technology Stack

- Odoo 17 Enterprise / Community
- Python
- PostgreSQL
- JavaScript (Odoo Web Client)
- XML (Views & Reports)
- XLSX Reporting Engine

---

## Development Approach

The project follows a clean modular architecture:

- Core Odoo code is never modified directly
- Each business feature is implemented as a separate module
- Customizations are isolated for upgrade compatibility
- Reusable components are used across modules
- Business logic is separated from UI and reporting layers

This ensures long-term maintainability and easy future upgrades.

---

## Business Value

This ERP customization delivers:

- Streamlined HR operations
- Automated payroll processing
- Improved financial reporting accuracy
- Faster purchase workflow handling
- Enhanced decision-making through dashboards
- Better system usability and user experience

---

## About the Project

**Petroraq ERP Customization Suite** is designed to transform standard Odoo into a fully tailored enterprise solution aligned with real business workflows and operational requirements.

---

## Developer

**Salman Awan**

Odoo Developer | ERP/CRM Consultant | Python Engineer

Specialized in:

- Odoo ERP Development & Customization
- CRM & Sales Automation Systems
- ERP and CRM system implementation
- HR, Payroll & Attendance Solutions
- Accounting & Financial Modules
- Inventory, Purchase & Supply Chain Systems
- Manufacturing (MRP) Customization
- API Integrations (REST, third-party services)
- Business Process Automation
- Custom Module Architecture & Development
- Reporting (PDF, Excel, Dashboard Systems)
- Odoo Migration & Version Upgrades
- System Optimization & Performance Tuning
---

## Notes

All modules are developed following Odoo best practices with focus on stability, scalability, and maintainability. Each component can be deployed independently or as part of a full ERP solution.