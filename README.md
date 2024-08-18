# Voice Database App

## Overview
The Voice Database App is a sophisticated tool for logging activities and managing data entries in a SQL database. This app leverages voice diarization to identify users by their voice and allows them to log activities simply by speaking. It features a user-friendly interface that enables users to choose a table, add data entries, view all entries, and undo changes if necessary.

## Features
- **Voice-Driven Activity Logging:** Users can log activities by speaking. The app identifies the speaker and categorizes the activity in the database.
- **SQL Database Integration:** Connects to a SQL database, allowing users to manage tables and entries efficiently.
- **Voice Diarization:** Identifies users based on their voice samples.
- **Undo Functionality:** Allows users to undo changes to the database.
- **User-Friendly Interface:** Provides an intuitive interface for interacting with the database.

## Example Usage
A user might say, "I had pasta with marinara sauce and meatballs for dinner." The app will:
- Identify the speaker using voice diarization.
- Log "have dinner" in the activity section.
- Log "pasta with marinara sauce and meatballs" in the details section.

## Installation

### Prerequisites
- Python 3.7+
- SQLite or another supported SQL database
- Required Python packages (see `requirements.txt`)

### Setup
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/voice-database-app.git
   cd voice-database-app
