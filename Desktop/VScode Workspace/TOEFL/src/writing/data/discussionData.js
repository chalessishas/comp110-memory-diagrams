export const discussionPrompts = [
  {
    id: 1,
    professor: {
      name: 'Dr. Johnson',
      question: 'Universities today often compete fiercely to attract new students. Consequently, many institutions are spending significant portions of their budgets on non-academic amenities, such as luxury dormitories, state-of-the-art recreation centers, and high-end dining halls. Critics, however, argue that this money should be directed exclusively toward hiring better faculty, expanding libraries, and funding research. In your opinion, is it justifiable for universities to invest heavily in student amenities, or should the focus remain on academic resources?',
    },
    students: [
      {
        name: 'Sarah',
        opinion: 'I believe that investing in amenities is important because when students are happy and healthy mentally, they perform better in their classes. A good recreation center or comfortable living space can reduce stress and create a sense of community on campus.',
      },
      {
        name: 'Mark',
        opinion: 'I strongly disagree. The primary reason we pay for university is to get an education that prepares us for a career. Every dollar spent on a fancy gym or luxury dorm is a dollar taken away from hiring qualified professors or funding important research.',
      },
    ],
    sampleResponse: "I side with Mark's perspective that academic resources must take priority. While comfortable amenities can reduce student stress, as Sarah suggests, the core value of a university lies in the quality of its instruction and research output. A well-funded library or a renowned professor will impact a student's career trajectory far more than a luxury dormitory. However, I acknowledge that completely neglecting student well-being is counterproductive. A balanced approach is ideal: universities should ensure basic, functional living and recreational facilities while directing the majority of discretionary funds toward academic excellence. The primary measure of a university's worth should remain its educational outcomes, not the opulence of its facilities.",
    sampleScore: 5,
  },
  {
    id: 2,
    professor: {
      name: 'Prof. Williams',
      question: 'Many educational systems follow a traditional calendar with a long summer vacation of two to three months. However, some districts have adopted year-round schooling, where students attend school for the same total number of days but with shorter, more frequent breaks throughout the year. Which calendar system do you think is more beneficial for students, and why?',
    },
    students: [
      {
        name: 'Liam',
        opinion: 'Students undergo a tremendous amount of stress during the academic year, and they need a significant, uninterrupted block of time to truly decompress. Summer break also provides opportunities for employment, camps, and family travel that are essential for personal development.',
      },
      {
        name: 'Maya',
        opinion: 'Research has shown that extended breaks cause significant knowledge loss, often called the "summer slide." Frequent, shorter breaks throughout the year prevent burnout much more effectively than waiting nine exhausting months for a vacation.',
      },
    ],
    sampleResponse: "I find Maya's argument about the year-round calendar more compelling. The 'summer slide' is a well-documented phenomenon where students, particularly those from disadvantaged backgrounds, lose significant academic progress over long breaks, widening achievement gaps. Shorter, more frequent breaks can provide adequate rest without the cognitive cost of extended disengagement. While Liam raises a valid point about the value of summer experiences like employment and travel, these opportunities are not available to all students equally. A year-round calendar could promote greater equity by ensuring consistent learning. The minor adjustment to scheduling family activities seems a worthwhile trade-off for the academic benefits and reduced burnout that more regular breaks provide.",
    sampleScore: 5,
  },
  {
    id: 3,
    professor: {
      name: 'Dr. Chen',
      question: 'Biometric technologies such as facial recognition and fingerprint scanning are increasingly being used in everyday life, from unlocking smartphones to making payments. Some people welcome this technology for its convenience and security benefits, while others express concerns about privacy and the potential misuse of personal data. Do the benefits of using biometric technology for everyday tasks outweigh the potential privacy risks?',
    },
    students: [
      {
        name: 'Alex',
        opinion: 'Biometrics are unique to each individual and always with you, making everyday transactions not only faster but also significantly more secure than traditional passwords. The convenience factor alone makes adoption worthwhile.',
      },
      {
        name: 'Priya',
        opinion: 'If someone steals your password, you can simply change it. But if a database containing your fingerprint or facial scan is hacked, your biometric identity is compromised forever. This permanent vulnerability is simply too great a risk.',
      },
    ],
    sampleResponse: "Priya's concern about the irreversibility of biometric data breaches is the most critical issue in this debate. Alex is correct that biometrics offer genuine convenience and security against common threats like password phishing. However, the asymmetry of risk is profound: a compromised password is fixable, but a compromised fingerprint is not. As data breaches become increasingly common, centralizing citizens' permanent biometric identifiers creates an unacceptable single point of failure. I believe biometrics can be used responsibly for local authentication, such as unlocking a personal device where data is stored on-chip, but should not be used for centralized databases. The potential for permanent, irreversible identity theft outweighs the convenience benefits for high-stakes applications.",
    sampleScore: 5,
  },
]
