// ═══════════════════════════════════════════════════════════════
// CourseHub AI Teaching Content Quality Benchmark — Test Data
// ═══════════════════════════════════════════════════════════════
//
// 6 subjects × 5 KPs each = 30 test cases
// Each KP has ground truth facts for verifying AI output correctness
// Used by run.ts to generate content and score against rubrics

export interface TestKnowledgePoint {
  id: string;
  subject: string;
  courseTitle: string;
  title: string;
  content: string | null;
  // Ground truth: facts the AI MUST get right
  groundTruth: {
    correctFacts: string[];       // Statements that must be true in any correct question/answer
    commonMisconceptions: string[]; // Real student misconceptions (good MCQ distractors should hit these)
    expectedDifficulty: number;    // 1-5 expected range for this topic
    bloomLevels: BloomLevel[];     // Which cognitive levels are appropriate for this KP
    keyTerms: string[];            // Domain-specific terms that should appear
  };
  // Traps: things the AI commonly gets wrong for this KP
  knownAITraps: string[];
}

export type BloomLevel =
  | "remember"    // recall facts
  | "understand"  // explain concepts
  | "apply"       // use in new situations
  | "analyze"     // break down, compare
  | "evaluate"    // justify, critique
  | "create";     // design, construct

export type Subject = "calculus" | "physics" | "cs" | "economics" | "psychology" | "biology";

// ─── Subject 1: Calculus II ───────────────────────────────────

const calculus: TestKnowledgePoint[] = [
  {
    id: "calc-001",
    subject: "calculus",
    courseTitle: "Calculus II",
    title: "Integration by Parts",
    content: "Technique for integrating products of functions using the formula ∫u dv = uv - ∫v du",
    groundTruth: {
      correctFacts: [
        "∫u dv = uv - ∫v du",
        "Choose u as the function that simplifies when differentiated (LIATE rule: Log > Inverse trig > Algebraic > Trig > Exponential)",
        "∫x·eˣ dx = x·eˣ - eˣ + C",
        "Can require multiple applications (e.g., ∫x²·eˣ dx needs IBP twice)",
        "Tabular integration is a shortcut for repeated IBP",
      ],
      commonMisconceptions: [
        "Confusing which function to assign as u vs dv",
        "Forgetting the minus sign in the formula",
        "Thinking IBP always simplifies — sometimes it creates a loop (∫eˣ sin x dx)",
        "Not recognizing when to use IBP vs substitution",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["integration by parts", "LIATE", "tabular integration", "product rule"],
    },
    knownAITraps: [
      "AI may generate ∫eˣ dx = eˣ + C as an IBP example (trivial, doesn't need IBP)",
      "AI may state LIATE as a strict rule rather than a heuristic",
    ],
  },
  {
    id: "calc-002",
    subject: "calculus",
    courseTitle: "Calculus II",
    title: "Taylor Series Convergence",
    content: "Determining the radius and interval of convergence for Taylor/Maclaurin series using ratio test",
    groundTruth: {
      correctFacts: [
        "Ratio test: R = lim |aₙ/aₙ₊₁| as n→∞",
        "eˣ converges for all x (R = ∞)",
        "1/(1-x) converges for |x| < 1",
        "ln(1+x) converges for -1 < x ≤ 1",
        "Endpoints must be checked separately",
      ],
      commonMisconceptions: [
        "Assuming radius of convergence = interval of convergence (ignoring endpoints)",
        "Forgetting to check endpoint convergence separately",
        "Confusing absolute vs conditional convergence at endpoints",
        "Thinking all Taylor series converge everywhere",
      ],
      expectedDifficulty: 4,
      bloomLevels: ["apply", "analyze", "evaluate"],
      keyTerms: ["radius of convergence", "interval of convergence", "ratio test", "Maclaurin series"],
    },
    knownAITraps: [
      "AI may give wrong radius for arctan(x) series (R=1, not R=∞)",
      "AI may not distinguish absolute vs conditional convergence at endpoints",
    ],
  },
  {
    id: "calc-003",
    subject: "calculus",
    courseTitle: "Calculus II",
    title: "Improper Integrals",
    content: "Evaluating integrals with infinite limits or discontinuous integrands using limits",
    groundTruth: {
      correctFacts: [
        "∫₁^∞ 1/xᵖ dx converges iff p > 1 (p-test)",
        "∫₀^1 1/xᵖ dx converges iff p < 1",
        "Must split at discontinuities: ∫₋₁^1 1/x² dx diverges (can't ignore x=0)",
        "Comparison test: if 0 ≤ f(x) ≤ g(x) and ∫g converges, then ∫f converges",
      ],
      commonMisconceptions: [
        "Evaluating ∫₋₁^1 1/x² dx as -2 (applying FTC without checking discontinuity)",
        "Confusing p-test thresholds for Type I vs Type II integrals",
        "Thinking ∫₁^∞ 1/x dx converges because 1/x → 0",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["improper integral", "p-test", "comparison test", "divergent"],
    },
    knownAITraps: [
      "AI may compute ∫₋₁^1 1/x dx = 0 by symmetry (wrong — it diverges)",
    ],
  },
  {
    id: "calc-004",
    subject: "calculus",
    courseTitle: "Calculus II",
    title: "Polar Coordinates Area",
    content: "Computing area enclosed by polar curves using A = ½∫r² dθ",
    groundTruth: {
      correctFacts: [
        "A = ½ ∫ₐᵇ [r(θ)]² dθ",
        "Area between two curves: A = ½ ∫ₐᵇ [r₁²- r₂²] dθ",
        "Cardioid r = 1 + cos θ has area 3π/2",
        "Must find intersection points to determine integration bounds",
        "r can be negative — the curve traces through the origin",
      ],
      commonMisconceptions: [
        "Using A = ∫r dθ instead of A = ½∫r² dθ",
        "Forgetting the ½ factor",
        "Not accounting for curves that overlap or have negative r values",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "understand"],
      keyTerms: ["polar coordinates", "cardioid", "rose curve", "limacon"],
    },
    knownAITraps: [
      "AI may give wrong area for r = sin(2θ) (one petal = π/8, not π/4)",
    ],
  },
  {
    id: "calc-005",
    subject: "calculus",
    courseTitle: "Calculus II",
    title: "Partial Fractions Decomposition",
    content: "Decomposing rational functions into simpler fractions for integration",
    groundTruth: {
      correctFacts: [
        "Degree of numerator must be less than denominator (do polynomial division first if not)",
        "Distinct linear factors: A/(x-a) + B/(x-b)",
        "Repeated linear: A/(x-a) + B/(x-a)²",
        "Irreducible quadratic: (Ax+B)/(x²+bx+c)",
        "∫1/(x²+1) dx = arctan(x) + C",
      ],
      commonMisconceptions: [
        "Forgetting to do polynomial long division when degree(num) ≥ degree(denom)",
        "Using A/(x²+1) instead of (Ax+B)/(x²+1) for irreducible quadratics",
        "Not handling repeated roots correctly",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "remember"],
      keyTerms: ["partial fractions", "irreducible quadratic", "polynomial long division"],
    },
    knownAITraps: [
      "AI may decompose 1/(x²-1) as A/x + B/(x-1) instead of A/(x-1) + B/(x+1)",
    ],
  },
];

// ─── Subject 2: Physics (Mechanics) ──────────────────────────

const physics: TestKnowledgePoint[] = [
  {
    id: "phys-001",
    subject: "physics",
    courseTitle: "General Physics I: Mechanics",
    title: "Newton's Second Law and Free Body Diagrams",
    content: "F = ma applied to systems with multiple forces, friction, and inclined planes",
    groundTruth: {
      correctFacts: [
        "ΣF = ma (net force, not individual forces)",
        "Weight component along incline: mg sin θ",
        "Weight component normal to incline: mg cos θ",
        "Static friction: fₛ ≤ μₛN",
        "Kinetic friction: fₖ = μₖN (constant, not ≤)",
        "Normal force is NOT always mg",
      ],
      commonMisconceptions: [
        "Normal force always equals mg (wrong on inclines, accelerating elevators)",
        "Friction always opposes motion (static friction can cause motion, e.g., walking)",
        "Heavier objects fall faster (ignoring air resistance, they don't)",
        "Confusing mass and weight",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["free body diagram", "normal force", "static friction", "kinetic friction", "net force"],
    },
    knownAITraps: [
      "AI may say friction always opposes direction of motion (wrong for static friction)",
      "AI may compute normal force as mg on an inclined plane",
    ],
  },
  {
    id: "phys-002",
    subject: "physics",
    courseTitle: "General Physics I: Mechanics",
    title: "Conservation of Energy",
    content: "Work-energy theorem, kinetic and potential energy, conservative vs non-conservative forces",
    groundTruth: {
      correctFacts: [
        "KE = ½mv²",
        "Gravitational PE = mgh (near Earth's surface)",
        "Work-energy theorem: W_net = ΔKE",
        "For conservative forces: KE₁ + PE₁ = KE₂ + PE₂",
        "Friction is non-conservative — energy is lost to heat",
        "Spring PE = ½kx²",
      ],
      commonMisconceptions: [
        "Energy is 'used up' rather than converted",
        "Confusing force and energy (more force ≠ more energy)",
        "Forgetting that reference point for PE is arbitrary",
        "Applying conservation of energy when friction is present without accounting for heat",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["apply", "understand"],
      keyTerms: ["kinetic energy", "potential energy", "conservative force", "work-energy theorem"],
    },
    knownAITraps: [
      "AI may forget to include rotational KE in rolling problems",
      "AI may confuse elastic PE formula sign (½kx², always positive)",
    ],
  },
  {
    id: "phys-003",
    subject: "physics",
    courseTitle: "General Physics I: Mechanics",
    title: "Rotational Inertia and Torque",
    content: "τ = Iα, moment of inertia for common shapes, parallel axis theorem",
    groundTruth: {
      correctFacts: [
        "τ = r × F (torque = lever arm × force, perpendicular component)",
        "τ = Iα (rotational analog of F = ma)",
        "I_disk = ½MR² (solid disk/cylinder about center)",
        "I_sphere = ⅖MR² (solid sphere about center)",
        "Parallel axis theorem: I = I_cm + Md²",
      ],
      commonMisconceptions: [
        "Torque depends on total force, not perpendicular component",
        "Moment of inertia is the same as mass",
        "Forgetting parallel axis theorem when axis is off-center",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "remember"],
      keyTerms: ["torque", "moment of inertia", "parallel axis theorem", "angular acceleration"],
    },
    knownAITraps: [
      "AI may give I_hoop = ½MR² (wrong — I_hoop = MR², I_disk = ½MR²)",
      "AI may confuse solid sphere (⅖MR²) with hollow sphere (⅔MR²)",
    ],
  },
  {
    id: "phys-004",
    subject: "physics",
    courseTitle: "General Physics I: Mechanics",
    title: "Simple Harmonic Motion",
    content: "Mass-spring and pendulum oscillation, period, frequency, energy in SHM",
    groundTruth: {
      correctFacts: [
        "x(t) = A cos(ωt + φ)",
        "ω = √(k/m) for mass-spring",
        "T = 2π√(m/k) for mass-spring",
        "T = 2π√(L/g) for simple pendulum (small angle)",
        "Pendulum period is independent of mass",
        "Total energy = ½kA² (constant in ideal SHM)",
      ],
      commonMisconceptions: [
        "Pendulum period depends on mass (it doesn't for simple pendulum)",
        "Larger amplitude = longer period (wrong for SHM, true for large-angle pendulum)",
        "Velocity is maximum at maximum displacement (it's zero there)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["period", "frequency", "angular frequency", "amplitude", "phase"],
    },
    knownAITraps: [
      "AI may state T = 2π√(L/g) works for all angles (only valid for small θ)",
    ],
  },
  {
    id: "phys-005",
    subject: "physics",
    courseTitle: "General Physics I: Mechanics",
    title: "Momentum and Collisions",
    content: "Conservation of momentum, elastic vs inelastic collisions, impulse",
    groundTruth: {
      correctFacts: [
        "p = mv (momentum = mass × velocity)",
        "In ALL collisions, total momentum is conserved (if no external forces)",
        "Elastic: both KE and momentum conserved",
        "Perfectly inelastic: objects stick together, maximum KE loss",
        "Impulse J = FΔt = Δp",
        "In 2D collisions, momentum is conserved in each direction independently",
      ],
      commonMisconceptions: [
        "KE is always conserved in collisions (only in elastic)",
        "Heavier object always 'wins' in a collision",
        "Momentum conservation requires no forces (only no EXTERNAL forces)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["apply", "understand"],
      keyTerms: ["momentum", "impulse", "elastic collision", "inelastic collision"],
    },
    knownAITraps: [
      "AI may say energy is conserved in inelastic collisions",
    ],
  },
];

// ─── Subject 3: Computer Science (Data Structures) ───────────

const cs: TestKnowledgePoint[] = [
  {
    id: "cs-001",
    subject: "cs",
    courseTitle: "Data Structures and Algorithms",
    title: "Binary Search Tree Operations",
    content: "Insert, search, delete operations on BST with time complexity analysis",
    groundTruth: {
      correctFacts: [
        "Average case: O(log n) for search/insert/delete",
        "Worst case (degenerate/skewed): O(n)",
        "In-order traversal yields sorted output",
        "Delete node with two children: replace with in-order successor or predecessor",
        "BST property: left < root < right (for all descendants, not just children)",
      ],
      commonMisconceptions: [
        "BST always has O(log n) operations (wrong — depends on balance)",
        "BST property only applies to immediate children (wrong — applies to entire subtree)",
        "Deleting a node with two children is simple removal (need successor/predecessor swap)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze", "understand"],
      keyTerms: ["BST", "in-order traversal", "balanced tree", "time complexity", "degenerate tree"],
    },
    knownAITraps: [
      "AI may state BST search is always O(log n) without mentioning worst case",
      "AI may not explain in-order successor replacement for two-child deletion",
    ],
  },
  {
    id: "cs-002",
    subject: "cs",
    courseTitle: "Data Structures and Algorithms",
    title: "Hash Table Collision Resolution",
    content: "Chaining vs open addressing (linear probing, quadratic probing, double hashing)",
    groundTruth: {
      correctFacts: [
        "Chaining: each bucket stores a linked list of colliding elements",
        "Linear probing: h(k,i) = (h(k) + i) mod m — causes primary clustering",
        "Quadratic probing: h(k,i) = (h(k) + c₁i + c₂i²) mod m — causes secondary clustering",
        "Double hashing: h(k,i) = (h₁(k) + i·h₂(k)) mod m — no clustering",
        "Load factor α = n/m; chaining degrades at α > 1, open addressing at α > 0.7",
        "Average case with good hash: O(1) search, O(1) insert",
      ],
      commonMisconceptions: [
        "Hash tables always have O(1) operations (worst case is O(n))",
        "All collision resolution methods perform equally (clustering matters)",
        "Load factor doesn't affect performance (it does — critical threshold ~0.75)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "analyze"],
      keyTerms: ["hash collision", "chaining", "open addressing", "load factor", "clustering"],
    },
    knownAITraps: [
      "AI may confuse primary clustering (linear probing) with secondary clustering (quadratic)",
    ],
  },
  {
    id: "cs-003",
    subject: "cs",
    courseTitle: "Data Structures and Algorithms",
    title: "Graph Traversal: BFS vs DFS",
    content: "Breadth-first and depth-first search algorithms, applications, time/space complexity",
    groundTruth: {
      correctFacts: [
        "BFS uses a queue; DFS uses a stack (or recursion)",
        "BFS finds shortest path in unweighted graphs",
        "DFS is used for topological sorting, cycle detection, connected components",
        "Both are O(V + E) time for adjacency list representation",
        "BFS space: O(V) (worst case: all vertices in queue)",
        "DFS space: O(V) (recursion depth in worst case)",
      ],
      commonMisconceptions: [
        "DFS finds shortest paths (BFS does, not DFS)",
        "BFS and DFS have different time complexities (both are O(V+E))",
        "DFS always uses less memory than BFS (depends on graph structure)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["understand", "apply", "analyze"],
      keyTerms: ["BFS", "DFS", "adjacency list", "topological sort", "shortest path"],
    },
    knownAITraps: [
      "AI may say DFS finds shortest path in unweighted graphs",
    ],
  },
  {
    id: "cs-004",
    subject: "cs",
    courseTitle: "Data Structures and Algorithms",
    title: "Dynamic Programming: Optimal Substructure",
    content: "Identifying DP problems, memoization vs tabulation, common DP patterns",
    groundTruth: {
      correctFacts: [
        "Two conditions: optimal substructure + overlapping subproblems",
        "Memoization = top-down (recursive + cache)",
        "Tabulation = bottom-up (iterative, fill table)",
        "Fibonacci: naive O(2ⁿ) → DP O(n) time, O(1) space with rolling",
        "Longest Common Subsequence: O(mn) time and space",
        "0/1 Knapsack: O(nW) pseudo-polynomial time",
      ],
      commonMisconceptions: [
        "Greedy and DP are the same (greedy makes locally optimal choices, DP considers all)",
        "All recursive problems can be solved with DP (need overlapping subproblems)",
        "Memoization and tabulation always have same space complexity (tabulation can often be optimized)",
      ],
      expectedDifficulty: 4,
      bloomLevels: ["analyze", "apply", "evaluate"],
      keyTerms: ["optimal substructure", "overlapping subproblems", "memoization", "tabulation"],
    },
    knownAITraps: [
      "AI may classify greedy problems as DP (activity selection is greedy, not DP)",
      "AI may state 0/1 knapsack is polynomial (it's pseudo-polynomial)",
    ],
  },
  {
    id: "cs-005",
    subject: "cs",
    courseTitle: "Data Structures and Algorithms",
    title: "Sorting Algorithm Comparison",
    content: "Time/space complexity and stability of merge sort, quick sort, heap sort",
    groundTruth: {
      correctFacts: [
        "Merge sort: O(n log n) always, O(n) extra space, stable",
        "Quick sort: O(n log n) average, O(n²) worst, O(log n) space, unstable",
        "Heap sort: O(n log n) always, O(1) extra space, unstable",
        "Comparison-based sorting lower bound: Ω(n log n)",
        "Quick sort worst case: already sorted + naive pivot (first/last element)",
        "Radix sort: O(nk) where k = number of digits, not comparison-based",
      ],
      commonMisconceptions: [
        "Quick sort is always O(n log n) (it's O(n²) worst case)",
        "Merge sort is better than quick sort (QS has better cache performance in practice)",
        "Heap sort is the best because it's O(n log n) in-place (high constant factor, poor cache)",
        "Stability doesn't matter (it does for multi-key sorting)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["stable sort", "in-place", "comparison-based", "pivot", "divide and conquer"],
    },
    knownAITraps: [
      "AI may say quick sort is stable (it's not in standard implementations)",
      "AI may say heap sort is stable (it's not)",
    ],
  },
];

// ─── Subject 4: Microeconomics ───────────────────────────────

const economics: TestKnowledgePoint[] = [
  {
    id: "econ-001",
    subject: "economics",
    courseTitle: "Principles of Microeconomics",
    title: "Price Elasticity of Demand",
    content: "Measuring responsiveness of quantity demanded to price changes, elastic vs inelastic goods",
    groundTruth: {
      correctFacts: [
        "PED = %ΔQd / %ΔP",
        "|PED| > 1 → elastic; |PED| < 1 → inelastic; |PED| = 1 → unit elastic",
        "Perfectly inelastic: vertical demand curve (insulin, life-saving drugs)",
        "Perfectly elastic: horizontal demand curve (commodity in perfect competition)",
        "Revenue maximized when PED = -1 (unit elastic)",
        "Determinants: substitutes, necessity vs luxury, time horizon, share of budget",
      ],
      commonMisconceptions: [
        "Steep demand curve = inelastic (depends on scale of axes)",
        "Elasticity is constant along a linear demand curve (it changes along the curve)",
        "Higher price always means more revenue (depends on elasticity)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["understand", "apply", "analyze"],
      keyTerms: ["price elasticity", "elastic", "inelastic", "total revenue test"],
    },
    knownAITraps: [
      "AI may say elasticity is constant on a linear demand curve (wrong — it varies)",
    ],
  },
  {
    id: "econ-002",
    subject: "economics",
    courseTitle: "Principles of Microeconomics",
    title: "Consumer and Producer Surplus",
    content: "Measuring welfare, deadweight loss from taxes and price controls",
    groundTruth: {
      correctFacts: [
        "CS = area below demand curve, above price (willingness to pay minus actual price)",
        "PS = area above supply curve, below price (actual price minus cost)",
        "Total surplus = CS + PS (maximized at market equilibrium)",
        "Tax creates deadweight loss (DWL = ½ × tax × ΔQ)",
        "Price ceiling below equilibrium creates shortage and DWL",
        "Price floor above equilibrium creates surplus and DWL",
      ],
      commonMisconceptions: [
        "Tax burden falls on whoever pays the tax (burden depends on relative elasticity)",
        "Price controls help everyone (they create deadweight loss)",
        "Consumer surplus means profit (it's the difference between WTP and price paid)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["understand", "apply"],
      keyTerms: ["consumer surplus", "producer surplus", "deadweight loss", "price ceiling", "price floor"],
    },
    knownAITraps: [
      "AI may say DWL from tax = tax × Q (wrong — it's ½ × tax × ΔQ, a triangle)",
    ],
  },
  {
    id: "econ-003",
    subject: "economics",
    courseTitle: "Principles of Microeconomics",
    title: "Marginal Cost and Profit Maximization",
    content: "MC = MR condition for profit max, relationship between MC/ATC/AVC curves",
    groundTruth: {
      correctFacts: [
        "Profit max: MC = MR (in perfectly competitive firm, MR = P)",
        "MC intersects ATC at ATC's minimum (U-shaped ATC)",
        "Shutdown rule: P < AVC (short run) → stop producing",
        "Break-even: P = min(ATC)",
        "MC curve above AVC = firm's short-run supply curve",
      ],
      commonMisconceptions: [
        "Profit max means MC = P always (MC = MR, which only equals P in perfect competition)",
        "Producing where revenue > cost (should be where MR = MC at the margin)",
        "Firm should shut down if making losses (only if P < AVC)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["marginal cost", "marginal revenue", "profit maximization", "shutdown point"],
    },
    knownAITraps: [
      "AI may generalize MC = P to all market structures (only perfect competition)",
    ],
  },
  {
    id: "econ-004",
    subject: "economics",
    courseTitle: "Principles of Microeconomics",
    title: "Monopoly Pricing and Output",
    content: "Price-setting by monopolist, MR < P, deadweight loss of monopoly",
    groundTruth: {
      correctFacts: [
        "Monopolist faces downward-sloping demand → MR < P",
        "MR curve has twice the slope of linear demand curve",
        "Monopolist produces where MC = MR, charges from demand curve",
        "Monopoly creates DWL (produces less than socially optimal)",
        "Price discrimination can reduce DWL (perfect discrimination eliminates it)",
        "Monopolist has no supply curve (price is a choice, not given)",
      ],
      commonMisconceptions: [
        "Monopolist charges the highest possible price (they optimize MC = MR)",
        "Monopolies always make profit (can still have losses if ATC > P at optimal Q)",
        "Monopolist has a supply curve (they don't — they're price setters)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "apply", "analyze"],
      keyTerms: ["monopoly", "marginal revenue", "deadweight loss", "price discrimination"],
    },
    knownAITraps: [
      "AI may say monopolist maximizes by charging highest possible price",
    ],
  },
  {
    id: "econ-005",
    subject: "economics",
    courseTitle: "Principles of Microeconomics",
    title: "Game Theory: Nash Equilibrium",
    content: "Dominant strategies, Nash equilibrium, Prisoner's Dilemma",
    groundTruth: {
      correctFacts: [
        "Nash equilibrium: no player can improve by unilaterally changing strategy",
        "Prisoner's Dilemma: both defect is NE, but both cooperate is Pareto-superior",
        "Dominant strategy: best response regardless of opponent's action",
        "A game can have 0, 1, or multiple Nash equilibria",
        "Mixed strategy NE: randomize to make opponent indifferent",
      ],
      commonMisconceptions: [
        "Nash equilibrium is always the best outcome for all players (Prisoner's Dilemma proves otherwise)",
        "Every game has a Nash equilibrium in pure strategies (some only have mixed NE)",
        "Nash equilibrium means both players are happy (just means no unilateral deviation improves payoff)",
      ],
      expectedDifficulty: 4,
      bloomLevels: ["understand", "analyze", "evaluate"],
      keyTerms: ["Nash equilibrium", "dominant strategy", "Prisoner's Dilemma", "Pareto optimal"],
    },
    knownAITraps: [
      "AI may say NE is always Pareto optimal (it's not — Prisoner's Dilemma NE is Pareto-dominated)",
    ],
  },
];

// ─── Subject 5: Psychology (Cognitive) ───────────────────────

const psychology: TestKnowledgePoint[] = [
  {
    id: "psych-001",
    subject: "psychology",
    courseTitle: "Introduction to Cognitive Psychology",
    title: "Working Memory Model (Baddeley)",
    content: "Central executive, phonological loop, visuospatial sketchpad, episodic buffer",
    groundTruth: {
      correctFacts: [
        "Central executive: attentional control, coordinates slave systems",
        "Phonological loop: verbal/acoustic info, inner voice + inner ear",
        "Visuospatial sketchpad: visual and spatial info",
        "Episodic buffer (added 2000): integrates info from subsystems and LTM",
        "Working memory capacity: 7±2 items (Miller, 1956) — now estimated at 4±1 chunks (Cowan, 2001)",
      ],
      commonMisconceptions: [
        "Working memory = short-term memory (WM includes processing, STM is just storage)",
        "Working memory capacity is exactly 7 items (Miller's estimate, Cowan revised to ~4 chunks)",
        "The model hasn't been updated since 1974 (episodic buffer added in 2000)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand"],
      keyTerms: ["central executive", "phonological loop", "visuospatial sketchpad", "episodic buffer"],
    },
    knownAITraps: [
      "AI may state 7±2 as current capacity estimate (Cowan's 2001 revision: 4±1)",
      "AI may omit the episodic buffer (added later in 2000)",
    ],
  },
  {
    id: "psych-002",
    subject: "psychology",
    courseTitle: "Introduction to Cognitive Psychology",
    title: "Classical and Operant Conditioning",
    content: "Pavlov's experiment, Skinner box, reinforcement schedules, extinction",
    groundTruth: {
      correctFacts: [
        "Classical: CS paired with US → CS alone elicits CR (Pavlov, 1904)",
        "Operant: behavior modified by consequences (reinforcement or punishment)",
        "Positive reinforcement: add pleasant stimulus → increase behavior",
        "Negative reinforcement: remove aversive stimulus → increase behavior (NOT punishment)",
        "Variable ratio schedule produces highest, most resistance-to-extinction response rate",
        "Extinction: CR diminishes when CS no longer paired with US",
      ],
      commonMisconceptions: [
        "Negative reinforcement = punishment (negative reinforcement INCREASES behavior)",
        "Classical conditioning only works with food (any US-UR pair works)",
        "Extinction means forgetting (it's new learning — spontaneous recovery proves original learning persists)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "apply"],
      keyTerms: ["conditioned stimulus", "unconditioned response", "reinforcement schedule", "extinction"],
    },
    knownAITraps: [
      "AI may confuse negative reinforcement with punishment",
    ],
  },
  {
    id: "psych-003",
    subject: "psychology",
    courseTitle: "Introduction to Cognitive Psychology",
    title: "Cognitive Biases in Decision Making",
    content: "Availability heuristic, anchoring, confirmation bias, loss aversion (Kahneman & Tversky)",
    groundTruth: {
      correctFacts: [
        "Availability heuristic: judge frequency by ease of recall (plane crashes seem more common)",
        "Anchoring: initial value influences subsequent estimates, even if irrelevant",
        "Confirmation bias: seek/interpret info that confirms existing beliefs",
        "Loss aversion: losses loom ~2× larger than equivalent gains (Kahneman & Tversky, 1979)",
        "Framing effect: same info, different presentation → different decisions",
      ],
      commonMisconceptions: [
        "Cognitive biases are 'bugs' in thinking (they're usually efficient heuristics that sometimes misfire)",
        "Knowing about a bias eliminates it (awareness helps but doesn't fully deactivate)",
        "Anchoring only works with relevant numbers (even random numbers anchor estimates)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["understand", "apply", "analyze"],
      keyTerms: ["availability heuristic", "anchoring", "confirmation bias", "loss aversion", "framing effect"],
    },
    knownAITraps: [
      "AI may attribute all biases to Kahneman & Tversky (confirmation bias is from Wason, 1960)",
    ],
  },
  {
    id: "psych-004",
    subject: "psychology",
    courseTitle: "Introduction to Cognitive Psychology",
    title: "Stages of Memory (Encoding, Storage, Retrieval)",
    content: "Levels of processing (Craik & Lockhart), encoding specificity, retrieval cues",
    groundTruth: {
      correctFacts: [
        "Three stages: encoding → storage → retrieval",
        "Levels of processing (Craik & Lockhart, 1972): deeper processing = better memory",
        "Shallow: structural (font) < Phonemic (rhyme) < Semantic (meaning): deep",
        "Encoding specificity: retrieval cues most effective when they match encoding context",
        "Context-dependent memory: recall better in same environment as learning",
        "State-dependent memory: recall better in same physiological state",
      ],
      commonMisconceptions: [
        "Memory works like a video recorder (it's reconstructive, not reproductive)",
        "Repetition alone guarantees long-term memory (elaborative rehearsal matters more)",
        "Forgetting means information is deleted (often a retrieval failure, not storage loss)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand"],
      keyTerms: ["levels of processing", "encoding specificity", "elaborative rehearsal", "retrieval cue"],
    },
    knownAITraps: [
      "AI may present memory as lossless recording (it's constructive/reconstructive)",
    ],
  },
  {
    id: "psych-005",
    subject: "psychology",
    courseTitle: "Introduction to Cognitive Psychology",
    title: "Piaget's Stages of Cognitive Development",
    content: "Sensorimotor, preoperational, concrete operational, formal operational stages",
    groundTruth: {
      correctFacts: [
        "Sensorimotor (0-2): object permanence develops",
        "Preoperational (2-7): egocentrism, lack of conservation, symbolic play",
        "Concrete operational (7-11): conservation, logical thinking about concrete objects",
        "Formal operational (12+): abstract reasoning, hypothetical thinking",
        "Conservation: understanding quantity doesn't change with shape change",
      ],
      commonMisconceptions: [
        "All children reach all stages at exact ages (ages are approximate, some don't reach formal)",
        "Piaget's theory is universally accepted (Vygotsky's ZPD offers alternative view)",
        "Stages are discrete (there's overlap and gradual transition)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand"],
      keyTerms: ["object permanence", "egocentrism", "conservation", "formal operational"],
    },
    knownAITraps: [
      "AI may state rigid age boundaries (Piaget's ages are approximations)",
      "AI may not mention that some adults don't reach formal operational stage",
    ],
  },
];

// ─── Subject 6: Molecular Biology ────────────────────────────

const biology: TestKnowledgePoint[] = [
  {
    id: "bio-001",
    subject: "biology",
    courseTitle: "Molecular Biology",
    title: "DNA Replication",
    content: "Semi-conservative replication, leading/lagging strand, Okazaki fragments, enzymes",
    groundTruth: {
      correctFacts: [
        "Semi-conservative: each new DNA has one old + one new strand (Meselson-Stahl, 1958)",
        "DNA polymerase III synthesizes 5' → 3' (reads template 3' → 5')",
        "Leading strand: continuous synthesis toward replication fork",
        "Lagging strand: discontinuous (Okazaki fragments), away from fork",
        "Primase makes RNA primer; DNA pol I replaces primers; Ligase seals nicks",
        "Helicase unwinds double helix; SSB proteins prevent re-annealing",
      ],
      commonMisconceptions: [
        "DNA polymerase can synthesize 3' → 5' (it can only add to 3' end)",
        "Both strands are replicated the same way (leading is continuous, lagging is not)",
        "Replication errors are always harmful (most are caught by proofreading)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["remember", "understand", "apply"],
      keyTerms: ["helicase", "primase", "Okazaki fragments", "leading strand", "lagging strand"],
    },
    knownAITraps: [
      "AI may say DNA polymerase reads 5' → 3' (it synthesizes 5'→3', reads template 3'→5')",
    ],
  },
  {
    id: "bio-002",
    subject: "biology",
    courseTitle: "Molecular Biology",
    title: "Central Dogma: Transcription",
    content: "RNA polymerase, promoter recognition, mRNA processing (capping, splicing, polyadenylation)",
    groundTruth: {
      correctFacts: [
        "Central dogma: DNA → RNA → Protein",
        "RNA polymerase reads template 3' → 5', synthesizes mRNA 5' → 3'",
        "Promoter: TATA box (~-25) recognized by TFIID/TBP in eukaryotes",
        "mRNA processing: 5' cap (7-methylguanosine) + 3' poly-A tail + splicing",
        "Introns spliced out by spliceosome; exons joined in mature mRNA",
        "Alternative splicing: one gene can produce multiple proteins",
      ],
      commonMisconceptions: [
        "Introns are 'junk DNA' (they have regulatory roles, some encode snoRNAs)",
        "Transcription and translation happen simultaneously in eukaryotes (they do in prokaryotes, not eukaryotes)",
        "mRNA is ready to use right after transcription (needs processing in eukaryotes)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["remember", "understand"],
      keyTerms: ["RNA polymerase", "promoter", "intron", "exon", "spliceosome", "poly-A tail"],
    },
    knownAITraps: [
      "AI may say transcription and translation are always coupled (only in prokaryotes)",
    ],
  },
  {
    id: "bio-003",
    subject: "biology",
    courseTitle: "Molecular Biology",
    title: "Enzyme Kinetics: Michaelis-Menten",
    content: "Km, Vmax, Lineweaver-Burk plot, competitive vs noncompetitive inhibition",
    groundTruth: {
      correctFacts: [
        "v = Vmax[S] / (Km + [S])",
        "Km = substrate concentration at half-Vmax (indicates affinity — lower Km = higher affinity)",
        "Competitive inhibitor: increases apparent Km, Vmax unchanged (overcome by ↑ substrate)",
        "Noncompetitive inhibitor: Vmax decreases, Km unchanged",
        "Lineweaver-Burk: 1/v vs 1/[S], y-intercept = 1/Vmax, x-intercept = -1/Km",
      ],
      commonMisconceptions: [
        "Higher Km = higher enzyme affinity (opposite: lower Km = higher affinity)",
        "Competitive inhibitors permanently inactivate enzymes (they're reversible, overcome by substrate)",
        "All inhibitors are bad (many drugs are enzyme inhibitors: statins, ACE inhibitors)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["Michaelis-Menten", "Km", "Vmax", "competitive inhibition", "Lineweaver-Burk"],
    },
    knownAITraps: [
      "AI may say competitive inhibitors decrease Vmax (they increase Km, Vmax unchanged)",
    ],
  },
  {
    id: "bio-004",
    subject: "biology",
    courseTitle: "Molecular Biology",
    title: "Cell Signaling: GPCR Pathway",
    content: "G protein-coupled receptor mechanism, second messengers (cAMP, IP3, DAG)",
    groundTruth: {
      correctFacts: [
        "GPCR: 7-transmembrane domain receptor, largest receptor family",
        "Ligand binds → conformational change → G protein α-subunit exchanges GDP for GTP",
        "Gαs activates adenylyl cyclase → cAMP ↑ → PKA activation",
        "Gαi inhibits adenylyl cyclase → cAMP ↓",
        "Gαq activates phospholipase C → PIP2 → IP3 + DAG",
        "IP3 → Ca²⁺ release from ER; DAG → PKC activation",
      ],
      commonMisconceptions: [
        "All GPCRs activate the same pathway (Gs, Gi, Gq activate different effectors)",
        "Signal amplification doesn't happen (one receptor → many G proteins → many second messengers)",
        "GPCRs are always on the cell surface (they are, but some ligands are lipophilic and bind intracellularly)",
      ],
      expectedDifficulty: 4,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["GPCR", "G protein", "adenylyl cyclase", "cAMP", "phospholipase C", "second messenger"],
    },
    knownAITraps: [
      "AI may confuse Gαs (stimulatory) with Gαi (inhibitory)",
    ],
  },
  {
    id: "bio-005",
    subject: "biology",
    courseTitle: "Molecular Biology",
    title: "CRISPR-Cas9 Gene Editing",
    content: "Mechanism, guide RNA design, on-target vs off-target effects, applications",
    groundTruth: {
      correctFacts: [
        "Cas9 is an RNA-guided endonuclease that creates double-strand breaks",
        "Guide RNA (sgRNA) = crRNA + tracrRNA fused together (~20 nt targeting sequence)",
        "PAM sequence (NGG for SpCas9) required adjacent to target site",
        "DSB repair: NHEJ (error-prone, knockouts) or HDR (precise editing with template)",
        "Off-target effects: sgRNA may bind similar sequences elsewhere in genome",
      ],
      commonMisconceptions: [
        "CRISPR is 100% precise (off-target effects are a real concern)",
        "CRISPR was invented by humans (it's a natural bacterial immune system, adapted as tool)",
        "CRISPR can only knock out genes (can also insert, replace, regulate via dCas9)",
        "PAM is part of the guide RNA (PAM is on the target DNA, not the guide)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "apply", "evaluate"],
      keyTerms: ["Cas9", "guide RNA", "PAM", "NHEJ", "HDR", "off-target"],
    },
    knownAITraps: [
      "AI may say PAM is part of the guide RNA (it's on the target DNA strand)",
      "AI may overstate CRISPR precision without mentioning off-target effects",
    ],
  },
];

// ─── Export all test data ────────────────────────────────────

export const ALL_TEST_KPS: TestKnowledgePoint[] = [
  ...calculus,
  ...physics,
  ...cs,
  ...economics,
  ...psychology,
  ...biology,
];

export const TEST_SUBJECTS: Record<Subject, TestKnowledgePoint[]> = {
  calculus,
  physics,
  cs,
  economics,
  psychology,
  biology,
};

export const SUBJECT_LABELS: Record<Subject, string> = {
  calculus: "Calculus II (微积分)",
  physics: "General Physics (普通物理)",
  cs: "Data Structures & Algorithms (数据结构)",
  economics: "Microeconomics (微观经济学)",
  psychology: "Cognitive Psychology (认知心理学)",
  biology: "Molecular Biology (分子生物学)",
};
