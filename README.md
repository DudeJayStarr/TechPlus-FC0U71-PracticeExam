# TechPlus-FC0U71-PracticeExam (Python GUI)

This project is a Python/Tkinter practice exam simulator for the CompTIA Tech+ (FC0-U71) certification.

-📝 75 randomly selected questions from a pool of 100

-⏱️ 105-minute countdown timer (like the real exam)

-📊 Automatic scoring on a 100–900 scale (Pass = 650 or higher)

-🔍 Review mode with your answers vs. correct answers



**Features**



-🎯 Randomized Practice Tests – Each run selects 75 random questions.

-🖥️ Simple GUI – Clean and easy-to-use Tkinter-based interface.

-⏱️ Live Countdown Timer – 105 minutes, matching the exam format.

-📊 Auto-Grading Pass/Fail – Get your score instantly after finishing.

-🔍 Detailed Review Mode – Review screen with ✓ / ✗ marks for each question






**Getting Started**


1. Install Python

Download and install Python 3.8+ (https://www.python.org/downloads/)
.

2. Download & Run

Clone or download this repository.

Run the program:

**python techplus_practice_gui.py**


That’s it! The GUI will launch and you can begin your practice exam.


**Question Bank** (questions.json)


All exam questions are stored in questions.json.
The format is simple and easy to edit:

{
 
  "question": "Example question?",
  
  "options": ["Option A", "Option B", "Option C", "Option D"],
  
  "answer": 1
  
}


- question → the exam question text
- options → multiple choice options (list of strings)
- answer → the index of the correct option (0 = first, 1 = second, etc.)
  

**Contributing & Fixing Incorrect Data**


Want to help keep this practice test accurate and up-to-date?

1. Fork this repo
2. Edit questions.json to fix incorrect answers, add new questions, or improve clarity
3. Validate your JSON (https://jsonlint.com/)
4. Submit a Pull Request

Please include a short explanation or reference (like the official CompTIA objective) when fixing or adding questions.

**License**

This project is licensed under the MIT License.
You’re free to use, modify, and share it.
