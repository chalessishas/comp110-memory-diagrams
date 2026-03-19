export const emailPrompts = [
  {
    id: 1,
    situation:
      'You took your team to a new restaurant recommended by your coworker, Kevin, but the food was disappointing and the service was slow.',
    goals: [
      'Explain what was wrong with the restaurant',
      'Describe the team\'s reaction',
      'Suggest alternative lunch arrangements',
    ],
    recipient: 'Kevin',
    sampleResponse: `I wanted to follow up on our team lunch at the restaurant you recommended yesterday. Unfortunately, the experience did not go well. The food arrived nearly forty minutes after we ordered, and when it finally came, several dishes were cold and underseasoned. The pasta was overcooked and my colleague's fish was dry. As you can imagine, the team was quite disappointed. A few people had back-to-back meetings afterward and felt the long wait added unnecessary stress to an already busy day. Morale at the table was noticeably low by the end of the meal. Going forward, I think it would be better to stick with our usual spot on Oak Street, which has always been reliable and quick. If anyone suggests a new place next time, perhaps we could try it on a less hectic day.`,
    sampleScore: 5,
  },
  {
    id: 2,
    situation:
      'You missed an important quiz in your biology class because of a family emergency. You need to contact your professor, Dr. Martinez.',
    goals: [
      'Explain why you missed the quiz',
      'Ask about make-up options',
      'Offer to provide documentation',
    ],
    recipient: 'Dr. Martinez',
    sampleResponse: `I am writing to inform you that I was unable to attend class on Thursday and therefore missed the biology quiz scheduled for that day. A family emergency arose early that morning that required my immediate attention, and I had no opportunity to notify you in advance. I sincerely apologize for any inconvenience this may have caused. I understand that the quiz covered material that is central to the upcoming unit, and I am eager to demonstrate my understanding of the content. I would be very grateful if there were any possibility of completing a make-up quiz at a time that is convenient for you. I am available before or after class most days this week. Additionally, I am happy to provide any supporting documentation related to the emergency if that would be helpful or required by department policy. Thank you for your understanding.`,
    sampleScore: 5,
  },
  {
    id: 3,
    situation:
      'The neighbors in the apartment above yours have been playing loud music late at night for the past two weeks. You want to contact the building manager, Ms. Thompson.',
    goals: [
      'Describe the noise issue and when it occurs',
      'Explain how it affects your daily life',
      'Request a specific resolution',
    ],
    recipient: 'Ms. Thompson',
    sampleResponse: `I am writing to bring a noise disturbance to your attention that has been affecting my apartment for the past two weeks. The tenants in the unit directly above mine, Apartment 4B, have been playing loud music most nights between 11:00 PM and 2:00 AM. The bass is clearly audible through my ceiling even with my door closed. This has significantly disrupted my sleep, and I have been arriving at work exhausted nearly every day as a result. I have also found it difficult to focus in the evenings when I need to study or prepare for early morning responsibilities. I attempted to speak with the neighbors directly last week, but the situation has not improved. I would respectfully request that you speak with them about adhering to the building's quiet hours policy. If that does not resolve the issue, I would appreciate knowing what further steps are available to me.`,
    sampleScore: 5,
  },
]
