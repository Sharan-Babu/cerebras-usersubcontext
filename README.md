# Cerebras UserSubContext
Using cerebras fast LLM inference to create an effective orchestration layer that determines which parts of the context to use for the next turn in a conversation. Helps reduce input tokens cost while maintaining accuracy.

Please have a look at conversation flow and outputs below. The _'Selected Context for this Turn'_ expanders in photos 3 and 4 display which parts of the on-going conversation were included in the context for a particular turn. When talking about, say, scientific topics, the other irrelevent parts of the discussion were cleverly left out.


1.
<img width="789" alt="Screenshot 2024-12-16 at 7 57 30 PM" src="https://github.com/user-attachments/assets/14ac835b-7641-47e0-a348-49b5b878b198" />

-----

2.
<img width="804" alt="Screenshot 2024-12-16 at 7 57 36 PM" src="https://github.com/user-attachments/assets/29c57b02-f242-45fb-a67b-535041065872" />

-----

3.
<img width="810" alt="Screenshot 2024-12-16 at 7 57 41 PM" src="https://github.com/user-attachments/assets/f6a96d3e-0cd4-4406-b440-c272c1913224" />

-----

4.
<img width="663" alt="Screenshot 2024-12-16 at 8 03 08 PM" src="https://github.com/user-attachments/assets/70592f0b-13e1-492a-888a-224e7c407064" />
