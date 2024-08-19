# Log My Activities

## Overview
This app is a cute little tool designed to help enter data into a SQL database. It aims at helping users keep track of their activities during the day, together with their family/partner/teamate. With the help of a little voice sample, the app can accurately identify users by their voice, and it allows the user to log activities by speaking naturally. Instead of saying "Name: Bob, Activity: finish meeting, Details: with Charlie about deforestation in Europe", simply say, "I finished a meeting with Charlie about deforestation in Europe" and the app will automatically recognize the speaker, categorize the activity, identify the details, and log all of it into the database. 

In addition to all that fancy speech recognition, LLM stuff, the app also offers a cookie-cutter, user-friendly interface that lets the user to manually add/undo data entries. My motivation for this app is not to boost productivity but to satiate the mutual curiosity between my wife and me about how we spend our days, and how that will change when we add a new family member soon. 

## Features
- **Voice-Driven Activity Logging:** Users can log activities by speaking naturally. The app identifies the speaker and categorizes the activity in the database.
- **SQL Database Integration:** Connects to a SQL database, allowing users to manage tables and entries efficiently.
- **User-Friendly Interface:** Provides an intuitive interface for interacting with the database.
- **Undo Functionality:** Allows users to undo changes to the database.


## Example Usage
Alice and Bob are in a team doing a project. After Alice completes a task, say it's "make pasta with marinara sauce for dinner", Alice can say, "I made pasta with marinara sauce for dinner." The app will identify it's Alice who made dinner, and enter the following into the database.
- **Member:** Alice
- **Time:** [Time of recording]
- **Activity:** Make dinner
- **Details:** Pasta with marinara sauce

## Installation
1. **Install Ollama.**
2. **Use Ollama to install the `gemma2:2b-instruct-fp16` model (or some other model that you love)**
3. **The STT model, whisper, requires ffmpeg, which can be found [here](https://www.ffmpeg.org)**
4. **Install Python dependencies from `requirements.txt`.**
5. **Run main.py**
