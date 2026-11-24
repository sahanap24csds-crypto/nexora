# 🏛️ NEXORA – Campus Coordination OS

### Connect. Coordinate. Optimise.

## 📌 Introduction

NEXORA (Campus Coordination OS) is a smart campus event planning and coordination platform designed to simplify and streamline college event management.

Organising college events involves multiple activities such as event proposals, approvals, venue booking, participant registrations, payment tracking, committee responsibilities, budgeting, and reporting. Managing these activities separately can lead to communication gaps, scheduling conflicts, and inefficient coordination.

NEXORA brings these operations together into a single, centralised platform where students, faculty, HODs, and principals can collaborate through role-based workspaces.

The platform provides a structured workflow for managing events, tracking responsibilities, monitoring approvals, and maintaining event-related records through an interactive dashboard.

## 🎯 Problem Statement

College event management often involves multiple departments and stakeholders, making coordination difficult.

Common challenges include:

- Manual event planning and approval processes.
- Conflicts in venue availability and event scheduling.
- Difficulty tracking participant registrations and payments.
- Unclear committee responsibilities and task ownership.
- Lack of centralised expense and sponsorship records.
- Limited visibility into event progress and administrative activities.
- Time-consuming preparation of reports and records.

These challenges can result in delays, duplicated work, and inefficient utilisation of campus resources.

## 💡 Our Solution

NEXORA provides a unified campus coordination platform that connects different stakeholders and brings essential event management activities into one system.

It introduces:

1. **Role-Based Access:** Separate workspaces for Students, Faculty, HODs, and Principals.
2. **Event Approval Management:** A structured, sequential event approval workflow.
3. **Smart Venue Scheduling:** Venue availability checks, capacity matching, and conflict detection.
4. **Registration & Payment Tracking:** Participant registration records and payment status management.
5. **Committee Task Management:** Assignment and tracking of responsibilities.
6. **Finance & Sponsorship Management:** Expense tracking, budget monitoring, and sponsor records.
7. **Analytics & Reports:** Visual dashboards and consolidated data exports.

NEXORA aims to make campus event coordination more organised, transparent, and efficient.

## ✨ Key Features

### 1. Role-Based Access Control

NEXORA provides different workspaces based on the user's role.

Four profiles are supported:

- **Student:** Event proposals, registrations, calendar, campus blueprint, and committee tasks.
- **Faculty:** Student workspaces along with approval responsibilities, finance, sponsors, payment reviews, and date-block management.
- **HOD:** Faculty-level access along with analytics and venue master management.
- **Principal:** Final event approval, administrative access, audit records, and overall campus coordination views.

Each role receives access to the functionalities relevant to its responsibilities.

### 2. Centralised Command Center

- Provides an overview of the event portfolio.
- Displays pending approval activities.
- Highlights registration and payment alerts.
- Tracks open committee tasks.
- Provides a quick overview of venue-related information.
- Helps users monitor important event activities from one dashboard.

### 3. Event Planning & Approval Management

- Create and manage event proposals.
- Assign a sequential approval chain.
- Follow the approval process: Faculty Coordinator → HOD → Principal.
- Record approval, rejection, and request-for-changes decisions.
- Maintain comments and decision timestamps.
- Track event and registration lifecycle states.
- Ensure that each approver can decide only their assigned approval stage.

### 4. Campus Blueprint & Venue Management

- Provides an interactive miniature schematic of campus venue zones.
- Displays a venue directory with available information.
- Maintains venue capacities and facilities.
- Includes accessibility notes.
- Allows authorised users to add and maintain venue records.
- Helps users understand available campus spaces for event planning.

*Note: The campus blueprint is an illustrative schematic and not an official architectural floor plan.*

### 5. Calendar & Smart Venue Scheduling

- Displays the event agenda and scheduled activities.
- Allows date blocks for examinations, holidays, maintenance, and college events.
- Checks venue availability and overlapping bookings.
- Performs venue capacity checks.
- Provides basic slot feasibility checking.
- Ranks suitable venues based on capacity fit and facility requirements.

This helps reduce scheduling conflicts and improves campus resource planning.

### 6. Registrations & Payment Tracking

- Maintains participant registration records.
- Generates unique participant IDs.
- Prevents duplicate email registrations for the same event.
- Tracks individual participant payment statuses.
- Supports payment verification and rejection through reviewer actions.
- Identifies duplicate payment references.
- Highlights missing references and partial-payment states.
- Provides CSV export for registration and payment records.

### 7. Committee Task Management

- Assign responsibilities to named individuals.
- Organise tasks by committee.
- Set deadlines and priorities.
- Define task completion criteria.
- Track task progress through four statuses:
  - To Do
  - In Progress
  - Done
  - Blocked
- Monitor pending and completed responsibilities.

This improves accountability and makes committee coordination more structured.

### 8. Finance & Sponsorship Management

- Maintain an event expense ledger.
- Track planned and actual expenses.
- Monitor payment statuses.
- Maintain sponsor information and sponsorship commitments.
- Track committed sponsorship amounts separately from actual cash received.
- Organise financial records for individual events.

### 9. Analytics & Reports

- Provides database-backed descriptive analytics.
- Displays payment status distribution.
- Visualises approval status.
- Tracks event expenses.
- Analyses committee task completion.
- Displays active bookings by venue.
- Provides consolidated CSV data export.

These reports help stakeholders understand event operations and monitor administrative activities.

### 10. Admin & Audit Management

- Maintains a record of important administrative activities.
- Tracks sign-in and sign-out events.
- Records changes made within the application.
- Provides access to audit history.
- Supports downloading the local SQLite database.

This helps improve visibility into application activities and record management.

## ⚙️ How NEXORA Works

NEXORA follows a structured event coordination workflow.

### Step 1: Role-Based Sign-In

Users select their respective roles: Student, Faculty, HOD, or Principal.

Based on the selected role, the application displays the corresponding workspaces and permissions.

### Step 2: Event Proposal Creation

Students or authorised users create event proposals by entering relevant event details.

The application performs basic required-field checks and checks for venue overlaps and date-block conflicts.

### Step 3: Sequential Event Approval

The proposed event moves through a predefined approval workflow:

**Faculty Coordinator → HOD → Principal**

Each approver reviews the proposal and can approve it, reject it, or request changes.

The next approval stage becomes available only after the preceding approval is granted.

### Step 4: Venue & Schedule Management

The Calendar & Slots module checks venue availability, capacity requirements, and scheduling conflicts.

Users can also add examination, holiday, maintenance, and other date blocks to prevent unsuitable scheduling.

### Step 5: Participant Registration

Participant registration records are maintained with unique participant IDs.

The system checks for duplicate email registrations within the same event and maintains individual payment statuses.

### Step 6: Committee Task Assignment

Event responsibilities are assigned to committee members with specific owners, priorities, deadlines, and completion criteria.

Progress is monitored through the task management workflow.

### Step 7: Finance & Sponsorship Tracking

Event expenses, planned budgets, actual amounts, sponsor commitments, and received sponsorship amounts are maintained in the finance module.

### Step 8: Analytics & Reporting

The platform uses stored records to generate descriptive charts and consolidated reports.

Stakeholders can review event activities, payment statuses, approvals, expenses, and task progress through the analytics dashboard.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic and backend processing |
| Streamlit | Interactive web application and dashboard |
| SQLite | Local relational database and data persistence |
| Pandas | Data processing and tabular operations |
| Plotly | Interactive charts and visual analytics |
| Python Environment Variables | Role-based password configuration |

## 🖥️ How to Use

1. Open the NEXORA application.
2. Select your role: Student, Faculty, HOD, or Principal.
3. Sign in using the corresponding role credentials.
4. Navigate through the workspaces available for your role.
5. Create event proposals and follow the approval workflow.
6. Explore campus venues and check scheduling feasibility.
7. Manage participant registrations and payment records.
8. Assign committee responsibilities and monitor task progress.
9. Maintain event expenses and sponsorship information.
10. View analytics and export reports.

## 🔐 Security & Access Management

- Role-based workspace visibility.
- Separate password configuration for each role.
- Environment variables for storing role passwords.
- Temporary sign-in pause after five incorrect attempts.
- Sign-in and sign-out activity recorded in the audit log.
- Approval decisions restricted to the assigned approval stage.

**Note:** The current build uses shared passwords per role and is intended as a demonstration prototype, not production-grade authentication.

## ⚠️ Limitations

NEXORA is a functional campus coordination prototype. The following limitations should be considered:

- Authentication uses shared role passwords rather than individual user accounts.
- No password reset or persistent user sessions are implemented.
- Payment verification is performed through reviewer actions; no real payment gateway or bank/UPI integration is available.
- The public registration URL is displayed, but a fully functional external participant registration route is not implemented in this build.
- Email, WhatsApp, and SMS notifications are not integrated.
- The campus blueprint is illustrative and requires verified campus information for actual deployment.
- Academic calendars and holidays must be entered manually.
- QR-based attendance, event-day check-in, and volunteer attendance/performance tracking are not included.
- Financial reconciliation and production-grade security controls are not implemented.
- Analytics are descriptive and rule-based; the platform does not use machine-learning predictions.
- The application currently uses a local SQLite database and is not designed for production-grade concurrent multi-user deployment.

## 🔮 Future Enhancements

- Integration with college ERP and student information systems.
- Individual student and faculty accounts with secure authentication.
- Real-time notifications through email, WhatsApp, and SMS.
- Integration with payment gateways for automated payment verification.
- QR-based event registration and attendance management.
- Live venue availability and resource utilisation tracking.
- Automated academic calendar synchronisation.
- Advanced analytics for event performance and resource planning.
- Cloud database integration and secure multi-user deployment.
- AI-powered event scheduling and resource allocation recommendations.

## 🌍 Project Impact

NEXORA aims to transform traditional campus event coordination into a more organised and centralised digital process.

By connecting students, faculty, HODs, and principals through a common platform, it helps reduce administrative complexity, improve responsibility tracking, simplify event approvals, and support better utilisation of campus resources.

The platform can be adapted for colleges, universities, student organisations, and institutions that regularly organise events and manage multiple committees.

**Our Vision:** To create a connected, transparent, and efficient campus ecosystem where every event is easier to plan, coordinate, and manage.

---

**NEXORA – Connect. Coordinate. Optimise.** 🏛️
