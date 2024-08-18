# Voice Database App

## Overview
This App is a cute little tool facilitating data entries in a SQL database. It mainly aims to log activities of each member in a team. Using voice diarization, this app can identify users by their voice so that credit can be correctly assigned with as little effort in data entry as possible. It also has a user-friendly interface that enables users to choose a table, add data entries, view all entries, and undo changes if necessary.

## Features
- **Voice-Driven Activity Logging:** Users can log activities by speaking. The app identifies the speaker and categorizes the activity in the database.
- **Undo Functionality:** Allows users to undo changes to the database.
- **SQL Database Integration:** Connects to a SQL database, allowing users to manage tables and entries efficiently.
- **User-Friendly Interface:** Provides an intuitive interface for interacting with the database.

## Example Usage
Alice and Bob are in a team doing a project. After Alice completing a task, say it's "make pasta with marinara sauce for dinner", Alice can say, "I made pasta with marinara sauce for dinner." The app will identify it's Alice who made dinner, and enter the following to the database.
- **Member:** Alice
- **Time:** [Time of recording]
- **Activity:** Make dinner
- **Details:** Pasta with marinara sauce

## Installation
1. **Install Ollama.**
2. **Use Ollama to install the `gemma2:2b-instruct-fp16` model (or some other model you love)**
3. **Install Python dependencies from requirements.txt.**
4. **Run main.py**
