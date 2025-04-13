# LoveSims

**Compatibility in Romantic Relationships: Discovering Your “Best Match” through AI-Agent Simulations**  
By: Charlotte Zhu, Xingyi Zhang, Mateo Larrea

- [Proposal Document](https://docs.google.com/document/d/1t_eptHVRG8HG3ZpN9EcgMT3HyJPvA-cdw-VBTQjVEUA/edit?usp=sharing)  
- [Love Sims Demo: Diego & Riya](https://vimeo.com/1035385847?share=copy)  
- [Final Presentation Slides](https://docs.google.com/presentation/d/1S76VCuu9lB9-11tPI_XdH8zC3aPe2hmb6oZvpJKhx74/edit?usp=sharing)  

## Project Overview
LoveSims explores AI-driven simulations to assess compatibility in romantic relationships, aiming to provide a more meaningful alternative to traditional online dating. Inspired by *Black Mirror*'s "Hang the DJ," the project uses AI agents with unique personalities and relational preferences, simulating interactions in varied "test date" scenarios to analyze compatibility. Agents participate in these scenarios, adapting their behaviors and gathering insights through dynamic feedback, ultimately generating a ranked list of top matches for users. LoveSims leverages GPT-based agents to model key relationship dynamics, providing nuanced interactions that predict compatibility based on communication styles, attachment styles, and emotional intelligence. By emphasizing user-driven scenarios, LoveSims aspires to improve match quality through authentic relational simulations, grounded in empirical dating patterns and insights from social psychology.

## Research Question
How effectively can AI-agent simulations model romantic relationships, and what factors contribute to identifying an ideal partner?

## Expected Results
We anticipate that this project will:
- Demonstrate the capability of AI to simulate complex, emotionally resonant interactions.
- Offer insights into the dynamics of AI-human relational simulations.
- Inform future developments in personalized AI companionship, dating simulations, and AI-based relationship counseling.

## How to Run

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Split your terminal into two windows.

4. In the first terminal:
   ```bash
   cd lovesims-nextjs
   npm install
   npm run dev
   ```

5. In the second terminal:
   ```bash
   python3 main.py
   ```

Make sure to maintain proper indentation when running these commands.
