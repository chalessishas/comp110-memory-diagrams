// 2026 新托福 Practice Pack 6 — Reading Section

export const pack6 = {
  id: 'pack6',
  name: 'Practice Pack 6',
  modules: [
    // ═══ Module 1 ═══
    {
      id: 'pack6-m1',
      name: 'Module 1',
      time: 11 * 60 + 30,
      sections: [
        // --- Complete the Words ---
        {
          type: 'complete_words',
          id: 'pack6-m1-cw',
          title: 'Rain and Ecosystems',
          instructions: 'Fill in the missing letters in the paragraph.',
          paragraph: [
            { text: 'Rain is a crucial part of Earth\'s ecosystem, supporting both plant growth and animal survival.  As ' },
            { blank: 'itation', prefix: 'precip', answer: 'precipitation' },
            { text: ' falls ' },
            { blank: 'om', prefix: 'fr', answer: 'from' },
            { text: ' ' },
            { blank: 'ky', prefix: 'the s', answer: 'the sky' },
            { text: ', it ' },
            { blank: 'nishes', prefix: 'reple', answer: 'replenishes' },
            { text: ' water ' },
            { blank: 'rces', prefix: 'sou', answer: 'sources' },
            { text: ', nourishes ' },
            { blank: 'ation', prefix: 'veget', answer: 'vegetation' },
            { text: ', and ' },
            { blank: 'ains', prefix: 'sust', answer: 'sustains' },
            { text: ' wildlife.  Some ' },
            { blank: 'ions', prefix: 'reg', answer: 'regions' },
            { text: ' receive ' },
            { blank: 'dant', prefix: 'abun', answer: 'abundant' },
            { text: ' rainfall, ' },
            { blank: 'ile', prefix: 'wh', answer: 'while' },
            { text: ' others experience prolonged dry periods, affecting local environments.  Excessive rain can lead to floods, creating hazards for communities and natural habitats.  Despite occasional dangers, rainfall is essential for maintaining ecological balance, ensuring that plants and animals thrive in diverse climates around the world.' },
          ],
        },

        // --- Read in Daily Life: Maria's Email ---
        {
          type: 'daily_life',
          id: 'pack6-m1-dl1',
          title: 'Assignment Extension Request',
          material_type: 'email',
          material: {
            subject: 'Assignment Extension Request',
            from: 'Maria',
            to: 'Professor Kim',
            body: "Dear Professor Kim,\n\nI'm writing to request a two-day extension for the research paper. My laptop crashed and I lost three days of work. I have already started rewriting and can submit by Friday. Thank you for considering my request.\n\nBest regards,\nMaria",
          },
          questions: [
            {
              id: 11,
              text: 'What does Maria\'s mention of having "already started rewriting" suggest about her attitude?',
              options: [
                'Maria expects the professor to automatically approve her request.',
                'Maria is trying to make the professor feel sorry for her situation.',
                'Maria believes technical problems excuse students from meeting deadlines.',
                'Maria is taking responsibility and showing effort to complete the work.',
              ],
              correct: 3,
              question_type: 'inference',
              explanation: 'By mentioning she has "already started rewriting," Maria demonstrates proactive effort rather than passivity. She is not just explaining a problem — she is showing she is actively working toward a solution, which signals responsibility.',
            },
            {
              id: 12,
              text: 'What is Maria asking for?',
              options: [
                'Help recovering her lost computer files',
                'Additional time to complete an assignment',
                'Permission to submit a shorter research paper',
                'Technical support for her laptop problems',
              ],
              correct: 1,
              question_type: 'detail',
              explanation: 'Maria explicitly writes "I\'m writing to request a two-day extension for the research paper." She is asking for more time, not file recovery, a shorter paper, or tech support.',
            },
          ],
        },

        // --- Read in Daily Life: Heating Maintenance ---
        {
          type: 'daily_life',
          id: 'pack6-m1-dl2',
          title: 'Heating System Maintenance',
          material_type: 'email',
          material: {
            subject: 'Upcoming Heating System Maintenance – Tuesday, May 27',
            from: 'Robert Thompson',
            to: 'Ms. Gardner',
            body: "Dear Ms. Gardner,\n\nI hope you're doing well. I'm writing to inform you of a scheduled maintenance procedure on the office heating system, set to take place on Tuesday, May 27, from 8:00 A.M. to 5:00 P.M. This essential work is part of our seasonal inspection and efficiency upgrade initiative to ensure optimal performance during the colder months.\n\nPlease note that the heating system will be offline throughout the day, and indoor temperatures will drop noticeably. We recommend dressing in warm layers and advising your team to do the same. If any team members are particularly sensitive to cooler environments, remote work arrangements may be considered.\n\nAdditionally, as external technicians will be on-site, please ensure all confidential materials are secured appropriately.\n\nShould you have any questions, contact the maintenance team at 555-7264.\n\nWarm regards,\nRobert Thompson",
          },
          questions: [
            {
              id: 13,
              text: 'What is indicated about the office heating system?',
              options: [
                'It failed an inspection.',
                'It will not be functioning during maintenance.',
                'It is not working properly.',
                'It performs optimally.',
              ],
              correct: 1,
              question_type: 'detail',
              explanation: 'The email states "the heating system will be offline throughout the day." This directly indicates it will not be functioning during maintenance. There is no mention of it having failed an inspection or not working properly — the maintenance is scheduled and preventive.',
            },
            {
              id: 14,
              text: 'What can be inferred about the weather on May 27?',
              options: [
                'It will be cooler than the temperature at which the office is normally kept.',
                'It will be unusual for the season.',
                'It will require office workers to stay home rather than going to the office.',
                'It will change throughout the day.',
              ],
              correct: 0,
              question_type: 'inference',
              explanation: 'The email says "indoor temperatures will drop noticeably" when the heating is off, and recommends "dressing in warm layers." This implies the outdoor/unheated temperature is cooler than the office is normally kept. Remote work is only "considered" for sensitive employees, not required for everyone.',
            },
            {
              id: 15,
              text: 'Who will be performing maintenance?',
              options: [
                'Ms. Gardner',
                'Ms. Gardner\'s team members',
                'Professionals from another company',
                'Robert Thompson',
              ],
              correct: 2,
              question_type: 'detail',
              explanation: 'The email mentions "external technicians will be on-site," meaning professionals from outside the company. Robert Thompson is the sender, not the maintenance worker, and Ms. Gardner\'s team is asked to secure confidential materials, not perform repairs.',
            },
          ],
        },

        // --- Read an Academic Passage: Fungi ---
        {
          type: 'academic_passage',
          id: 'pack6-m1-ap',
          title: 'The Role of Fungi in Ecosystems',
          passage: `Fungi play a crucial role in ecosystems, often working behind the scenes to decompose organic matter and recycle nutrients. Unlike plants, fungi do not photosynthesize; instead, they obtain energy by breaking down dead plants and animals. This decomposition process is essential for nutrient cycling, as it releases vital elements like nitrogen and phosphorus back into the soil, supporting new plant growth. Their role in nutrient cycling is indispensable for healthy ecosystems.

One fascinating group of fungi is mycorrhizal fungi, which form symbiotic relationships with plant roots. These fungi extend the root system of plants, allowing them to access water and nutrients more efficiently. In return, the plants provide the fungi with carbohydrates produced through photosynthesis. This mutually beneficial relationship enhances plant growth and resilience, particularly in nutrient-poor soils.

Not all fungi are beneficial. Some pathogenic fungi cause diseases in plants and animals, leading to significant agricultural and ecological impacts. For example, the chytrid fungus has devastated amphibian populations worldwide. Understanding the diverse roles of fungi in ecosystems can help scientists develop strategies to mitigate their negative effects while leveraging their benefits for environmental sustainability.`,
          questions: [
            {
              id: 16,
              paragraph: 1,
              text: 'According to the passage, fungi are beneficial to plants in terms of',
              options: [
                'helping plants to decompose organic matter',
                'making it possible for plants to photosynthesize',
                'reducing the amount of nitrogen and phosphorus inside plants',
                'helping plants to obtain nutrients',
              ],
              correct: 3,
              question_type: 'detail',
              explanation: 'Paragraph 2 describes mycorrhizal fungi that "extend the root system of plants, allowing them to access water and nutrients more efficiently." This directly supports option D. Fungi decompose matter themselves (not helping plants do it), and the passage says fungi don\'t photosynthesize.',
            },
            {
              id: 17,
              paragraph: 0,
              text: 'The word "indispensable" in the passage is closest in meaning to',
              options: [
                'similar',
                'well-known',
                'essential',
                'useful',
              ],
              correct: 2,
              question_type: 'vocab',
              highlighted_word: 'indispensable',
              explanation: '"Indispensable" means absolutely necessary or essential — something you cannot do without. The sentence says fungi\'s role "is indispensable for healthy ecosystems," meaning it is essential/required. "Useful" is too weak; "similar" and "well-known" are unrelated.',
            },
            {
              id: 18,
              paragraph: null,
              text: 'Which of the following is NOT mentioned in the passage as a process performed by fungi?',
              options: [
                'Decomposing organic matter',
                'Releasing nitrogen and phosphorus into the soil',
                'Forming important relationships with plant roots',
                'Producing their own food',
              ],
              correct: 3,
              question_type: 'detail',
              explanation: 'The passage explicitly states fungi "do not photosynthesize" — they cannot produce their own food. All other options are directly mentioned: decomposing organic matter (P1), releasing nitrogen/phosphorus (P1), and forming relationships with plant roots (P2).',
            },
            {
              id: 19,
              paragraph: 2,
              text: 'What can be inferred about the diverse roles of fungi?',
              options: [
                'This diversity makes fungi especially difficult for scientists to understand.',
                'This diversity is considered to be important for the ongoing health of the environment.',
                'This diversity will decline when harmful fungi are eliminated.',
                'This diversity has been linked to the sustainability of amphibian populations.',
              ],
              correct: 1,
              question_type: 'inference',
              explanation: 'The passage concludes that understanding fungi\'s diverse roles can help "leveraging their benefits for environmental sustainability." This implies their diversity is important for environmental health. The chytrid fungus devastated amphibians — fungi diversity isn\'t linked to amphibian sustainability.',
            },
            {
              id: 20,
              paragraph: 1,
              text: 'What can be inferred about mycorrhizal fungi?',
              options: [
                'They compete with plants for carbohydrates.',
                'They help plants absorb nutrients.',
                'They decompose dead plants and animals.',
                'They can cause diseases in plants.',
              ],
              correct: 1,
              question_type: 'inference',
              explanation: 'Paragraph 2 says mycorrhizal fungi "extend the root system of plants, allowing them to access water and nutrients more efficiently." This means they help plants absorb nutrients. They receive carbohydrates from plants (not compete for them). Decomposition and disease are roles of other fungi types.',
            },
          ],
        },
      ],
    },

    // ═══ Module 2 ═══
    {
      id: 'pack6-m2',
      name: 'Module 2',
      time: 9 * 60,
      sections: [
        // --- Complete the Words ---
        {
          type: 'complete_words',
          id: 'pack6-m2-cw',
          title: 'Volcanoes',
          instructions: 'Fill in the missing letters in the paragraph.',
          paragraph: [
            { text: 'Volcanoes are openings in Earth\'s crust through which molten rock, ash, and gases are ejected.  Volcanic ' },
            { blank: 'tions', prefix: 'erup', answer: 'eruptions' },
            { text: ' can ' },
            { blank: 'ate', prefix: 'cre', answer: 'create' },
            { text: ' islands, ' },
            { blank: 'tains', prefix: 'moun', answer: 'mountains' },
            { text: ', and ' },
            { blank: 'her', prefix: 'ot', answer: 'other' },
            { text: ' landforms, but ' },
            { blank: 'ey', prefix: 'th', answer: 'they' },
            { text: ' can ' },
            { blank: 'so', prefix: 'al', answer: 'also' },
            { text: ' be ' },
            { blank: 'uctive', prefix: 'destr', answer: 'destructive' },
            { text: ', causing ' },
            { blank: 'age', prefix: 'dam', answer: 'damage' },
            { text: ' to ' },
            { blank: 'by', prefix: 'near', answer: 'nearby' },
            { text: ' areas.  ' },
            { blank: 'ying', prefix: 'Stud', answer: 'Studying' },
            { text: ' volcanoes helps scientists understand Earth\'s internal processes: for example, how volcanoes form at tectonic plate boundaries or over hotspots in the mantle and how magma rises up from the mantle and erupts as lava on the surface.' },
          ],
        },

        // --- Read an Academic Passage: Renewable Energy ---
        {
          type: 'academic_passage',
          id: 'pack6-m2-ap',
          title: 'Renewable Energy Sources',
          passage: `Renewable energy sources, such as solar, wind, and hydroelectric power, are increasingly gaining attention as alternatives to fossil fuels. Solar panels convert sunlight into electricity, providing a clean and abundant energy source. Wind turbines harness the power of wind, while hydroelectric plants use flowing water to generate electricity. These technologies offer significant environmental benefits, including reduced greenhouse gas emissions and decreased reliance on non-renewable resources.

However, renewable energy is not without its challenges. Solar and wind energy are intermittent, meaning they can be inconsistent depending on weather conditions. This intermittency requires the development of advanced storage solutions to ensure a steady supply of electricity. Additionally, the initial cost of installing renewable energy infrastructure can be high, although long-term savings and environmental benefits often outweigh this investment.

Recent innovations are addressing these issues. For instance, researchers are developing more efficient solar panels and energy storage systems that can store excess power generated during peak times. Wind turbines are being designed to operate in lower wind speeds, increasing their efficiency. Governments and private companies are also investing in renewable energy projects, recognizing the importance of transitioning to sustainable energy sources.`,
          questions: [
            {
              id: 11,
              paragraph: 0,
              text: 'Which of the following is mentioned in the passage as one environmental benefit of renewable energy sources?',
              options: [
                'They lower the amount of greenhouse gas produced.',
                'They provide a steady supply of electricity.',
                'They are easy to install.',
                'They can operate in all weather conditions.',
              ],
              correct: 0,
              question_type: 'detail',
              explanation: 'Paragraph 1 explicitly lists "reduced greenhouse gas emissions" as an environmental benefit. A "steady supply" is actually a challenge (paragraph 2 discusses intermittency). The passage never says they are easy to install or work in all weather.',
            },
            {
              id: 12,
              paragraph: 1,
              text: 'What challenge is associated with solar and wind energy?',
              options: [
                'High greenhouse gas emissions',
                'Inconsistent energy production',
                'Excessive reliance on fossil fuels',
                'Limited technological development',
              ],
              correct: 1,
              question_type: 'detail',
              explanation: 'Paragraph 2 states solar and wind energy "are intermittent, meaning they can be inconsistent depending on weather conditions." This directly matches "inconsistent energy production." Renewable energy reduces greenhouse gas emissions, not increases them.',
            },
            {
              id: 13,
              paragraph: 2,
              text: 'How are researchers addressing the issue of energy intermittency?',
              options: [
                'By developing more efficient solar panels',
                'By decreasing the cost of installation',
                'By using fossil fuels as a backup',
                'By limiting the use of renewable energy',
              ],
              correct: 0,
              question_type: 'detail',
              explanation: 'Paragraph 3 says "researchers are developing more efficient solar panels and energy storage systems." While storage directly addresses intermittency, the question asks about researchers\' approach, and developing better solar panels is explicitly mentioned. Fossil fuel backup and limiting use are never discussed.',
            },
            {
              id: 14,
              paragraph: 0,
              text: 'The word "reliance" in the passage is closest in meaning to',
              options: [
                'dependence',
                'trust',
                'use',
                'production',
              ],
              correct: 0,
              question_type: 'vocab',
              highlighted_word: 'reliance',
              explanation: '"Reliance" means the state of depending on something. "Decreased reliance on non-renewable resources" means reduced dependence on them. While "trust" is a related sense of the word, in this context it refers to dependence/need, not confidence.',
            },
            {
              id: 15,
              paragraph: 2,
              text: 'What is the author\'s purpose in mentioning "recent innovations"?',
              options: [
                'To highlight the drawbacks of renewable energy',
                'To suggest that fossil fuels are still necessary',
                'To describe solutions to the challenges of renewable energy',
                'To argue that the cost of renewable energy is too high',
              ],
              correct: 2,
              question_type: 'purpose',
              highlighted_word: 'Recent innovations',
              explanation: 'Paragraph 3 opens with "Recent innovations are addressing these issues" — "these issues" refers to the challenges discussed in paragraph 2 (intermittency and cost). The purpose is to show that solutions exist, not to criticize renewable energy or promote fossil fuels.',
            },
          ],
        },
      ],
    },
  ],
};
