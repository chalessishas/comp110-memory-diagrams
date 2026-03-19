export const passage = `Urban agriculture, the practice of cultivating crops and raising livestock within city boundaries, has emerged as a significant solution to food security challenges in densely populated areas. Traditionally, food production has been concentrated in rural regions, with cities entirely dependent on distant supply chains. However, mounting environmental concerns and the growing demand for local, sustainable food sources have prompted urban planners and agricultural experts to reconsider this model.

One of the primary advantages of urban farming is its capacity to reduce transportation costs and carbon emissions associated with food distribution. When vegetables and fruits are grown locally within city limits, they reach consumers with minimal processing and shorter delivery times, maintaining superior nutritional quality. Additionally, urban farms create green spaces that improve air quality, reduce urban heat island effects, and provide recreational opportunities for residents—benefits that extend beyond mere food production.

Despite these benefits, implementing urban agriculture in cities presents considerable challenges. Space constraints remain the most obvious obstacle; cities lack the vast acreage required for traditional agriculture. To overcome this limitation, innovative farming techniques such as vertical farming and hydroponics have gained prominence. These methods involve growing plants in stacked, controlled environments using nutrient-rich water instead of soil, significantly increasing yield per square foot. Some research suggests that vertical farms can produce up to 10 times more food per acre compared to conventional farms.

However, the economic viability of these advanced techniques is still questionable. The initial infrastructure costs are substantial, and energy consumption for maintaining optimal growing conditions remains high. Furthermore, the regulatory environment surrounding urban farming varies considerably by city, creating inconsistency in implementation. Some municipalities actively support urban agriculture through zoning reforms and financial incentives, while others impose strict regulations that hinder development.

Nevertheless, successful case studies from cities like Singapore, Amsterdam, and Toronto demonstrate that urban agriculture can be both economically feasible and environmentally beneficial when properly supported. These cities have integrated farming into urban development strategies, resulting in improved food security and community engagement. As urbanization continues globally, urban agriculture is likely to become an essential component of sustainable city planning rather than merely a supplementary trend.`;

export const questions = [
  {
    id: 1,
    type: 'vocab',
    paragraph: 0,
    text: 'The word "mounting" in paragraph 1 is closest in meaning to:',
    options: ['Climbing', 'Increasing', 'Installing', 'Supporting'],
    correct: 1,
    explanation: '"Mounting" in this context means growing or increasing in intensity. The passage describes environmental concerns that are becoming greater over time.',
  },
  {
    id: 2,
    type: 'detail',
    paragraph: 1,
    text: 'According to the passage, which of the following is a benefit of local urban farming?',
    options: ['Requires no regulatory approval', 'Maintains higher nutritional quality', 'Eliminates all transportation costs', 'Produces crops with more pesticides'],
    correct: 1,
    explanation: 'The passage states that locally grown produce reaches consumers "maintaining superior nutritional quality" due to minimal processing and shorter delivery times.',
  },
  {
    id: 3,
    type: 'vocab',
    paragraph: 3,
    text: 'The word "viable" in paragraph 4 most closely means:',
    options: ['Profitable', 'Practical', 'Feasible', 'Complex'],
    correct: 2,
    explanation: '"Viable" means capable of working successfully; feasible. The passage questions whether advanced farming techniques can be practically sustained.',
  },
  {
    id: 4,
    type: 'inference',
    paragraph: 2,
    text: 'Based on the passage, what can be inferred about vertical farming?',
    options: ['It has completely replaced traditional farming', 'It solves space issues but has economic challenges', 'It requires no energy to operate', 'It is used in most cities worldwide'],
    correct: 1,
    explanation: 'The passage indicates vertical farming addresses space constraints (paragraph 3) but faces economic viability questions (paragraph 4).',
  },
  {
    id: 5,
    type: 'detail',
    paragraph: 2,
    text: 'How much more food can vertical farms produce compared to conventional farms?',
    options: ['2 times', '5 times', '10 times', 'The passage does not specify'],
    correct: 2,
    explanation: 'The passage directly states: "vertical farms can produce up to 10 times more food per acre compared to conventional farms."',
  },
  {
    id: 6,
    type: 'attitude',
    paragraph: null,
    text: "The author's attitude toward urban agriculture can best be described as:",
    options: ['Dismissive', 'Enthusiastically supportive', 'Cautiously optimistic', 'Completely negative'],
    correct: 2,
    explanation: 'The author acknowledges both benefits and challenges, yet concludes positively — a hallmark of cautious optimism.',
  },
  {
    id: 7,
    type: 'inference',
    paragraph: 3,
    text: 'Which of the following does the passage suggest about regulations?',
    options: ['All cities have supportive agricultural policies', 'Regulatory policies differ among cities', 'No regulations exist for urban farming', 'Strong regulations prevent all urban farming'],
    correct: 1,
    explanation: 'The passage states "the regulatory environment surrounding urban farming varies considerably by city," indicating inconsistency across municipalities.',
  },
  {
    id: 8,
    type: 'detail',
    paragraph: 1,
    text: 'The passage mentions all of the following as benefits of urban farming EXCEPT:',
    options: ['Improved air quality', 'Reduced transportation emissions', 'Guaranteed food affordability', 'Recreational opportunities for residents'],
    correct: 2,
    explanation: 'The passage never mentions guaranteed food affordability. It discusses air quality, reduced emissions, and recreational opportunities.',
  },
  {
    id: 9,
    type: 'vocab',
    paragraph: 4,
    text: 'The phrase "case studies" in paragraph 5 refers to:',
    options: ['Written examinations', 'Specific examples used for analysis', 'Legal documents', 'Financial reports'],
    correct: 1,
    explanation: '"Case studies" are detailed analyses of specific instances — here referring to real-world examples of successful urban agriculture in particular cities.',
  },
  {
    id: 10,
    type: 'multiple',
    paragraph: 4,
    text: 'Which of the following are mentioned in the passage as cities with successful urban agriculture models? (Select 3)',
    options: ['Singapore', 'Amsterdam', 'Toronto', 'Beijing', 'Paris', 'Sydney'],
    correct: [0, 1, 2],
    explanation: 'The passage specifically names Singapore, Amsterdam, and Toronto as cities with successful urban agriculture case studies.',
  },
];

export const typeLabels = {
  vocab: 'Vocabulary',
  detail: 'Factual Detail',
  inference: 'Inference',
  attitude: 'Author Attitude',
  purpose: 'Author Purpose',
  negative_fact: 'Negative Fact',
  multiple: 'Select Multiple',
};

export const typeColors = {
  vocab: { bg: 'rgba(191, 131, 72, 0.08)', text: '#b87333', border: 'rgba(191, 131, 72, 0.2)' },
  detail: { bg: 'rgba(82, 130, 175, 0.08)', text: '#4a7fa5', border: 'rgba(82, 130, 175, 0.2)' },
  inference: { bg: 'rgba(130, 100, 170, 0.08)', text: '#7a5fb0', border: 'rgba(130, 100, 170, 0.2)' },
  attitude: { bg: 'rgba(100, 150, 120, 0.08)', text: '#5a9a6e', border: 'rgba(100, 150, 120, 0.2)' },
  purpose: { bg: 'rgba(80, 140, 160, 0.08)', text: '#4a8fa0', border: 'rgba(80, 140, 160, 0.2)' },
  negative_fact: { bg: 'rgba(160, 100, 80, 0.08)', text: '#a06850', border: 'rgba(160, 100, 80, 0.2)' },
  multiple: { bg: 'rgba(170, 100, 100, 0.08)', text: '#b06060', border: 'rgba(170, 100, 100, 0.2)' },
};
