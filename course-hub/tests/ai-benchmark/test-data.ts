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

export type Subject = "calculus" | "physics" | "cs" | "economics" | "psychology" | "biology" | "cn_history" | "cn_literature";

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

// ─── Subject 7: 中国近现代史 (Chinese-only subject) ────────────
// Tests Chinese-specific domain knowledge and Chinese output quality

const cn_history: TestKnowledgePoint[] = [
  {
    id: "cnhist-001",
    subject: "cn_history",
    courseTitle: "中国近现代史纲要",
    title: "鸦片战争与《南京条约》",
    content: "鸦片战争背景、经过、《南京条约》内容及其对中国社会的影响",
    groundTruth: {
      correctFacts: [
        "鸦片战争时间：1840-1842年",
        "《南京条约》是中国近代史上第一个不平等条约",
        "割让香港岛（非九龙、非新界）",
        "开放广州、厦门、福州、宁波、上海五口通商",
        "赔款2100万银元",
        "协定关税：中国丧失关税自主权",
      ],
      commonMisconceptions: [
        "鸦片战争割让了整个香港（只割让了香港岛，九龙半岛是1860年《北京条约》）",
        "林则徐虎门销烟是战争的唯一原因（更深层是贸易逆差和市场开放需求）",
        "《南京条约》包含领事裁判权（领事裁判权是后续《虎门条约》的内容）",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["不平等条约", "五口通商", "协定关税", "割让香港岛", "2100万银元"],
    },
    knownAITraps: [
      "AI 可能混淆香港岛与整个香港的割让时间",
      "AI 可能将领事裁判权归入《南京条约》（实为《虎门条约》附件）",
    ],
  },
  {
    id: "cnhist-002",
    subject: "cn_history",
    courseTitle: "中国近现代史纲要",
    title: "辛亥革命与中华民国建立",
    content: "同盟会、武昌起义、中华民国临时政府、《临时约法》、袁世凯窃国",
    groundTruth: {
      correctFacts: [
        "武昌起义时间：1911年10月10日",
        "孙中山于1912年1月1日就任中华民国临时大总统",
        "《中华民国临时约法》确立了三权分立的共和政体",
        "清帝溥仪于1912年2月12日退位",
        "袁世凯就任临时大总统后逐步走向独裁",
        "辛亥革命推翻了两千多年的封建帝制",
      ],
      commonMisconceptions: [
        "辛亥革命彻底改变了中国社会性质（没有，中国仍是半殖民地半封建社会）",
        "孙中山领导了武昌起义（起义时孙中山在海外，事后被推举为临时大总统）",
        "辛亥革命是资产阶级革命的成功（推翻帝制成功，但民主共和遭袁世凯破坏）",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["remember", "understand", "evaluate"],
      keyTerms: ["武昌起义", "临时约法", "三权分立", "封建帝制", "半殖民地半封建"],
    },
    knownAITraps: [
      "AI 可能说孙中山直接领导了武昌起义（他当时不在国内）",
      "AI 可能夸大辛亥革命的社会变革深度",
    ],
  },
  {
    id: "cnhist-003",
    subject: "cn_history",
    courseTitle: "中国近现代史纲要",
    title: "五四运动",
    content: "巴黎和会、学生示威、新文化运动的延续、马克思主义传播",
    groundTruth: {
      correctFacts: [
        "1919年5月4日爆发于北京",
        "直接导火索：巴黎和会上中国外交失败（山东问题）",
        "口号：「外争主权，内除国贼」",
        "前期以学生为主力，后期工人阶级登上历史舞台",
        "五四运动是中国新民主主义革命的开端",
        "促进了马克思主义在中国的广泛传播",
      ],
      commonMisconceptions: [
        "五四运动 = 新文化运动（五四运动是新文化运动的延续和发展，但不等同）",
        "五四运动只是学生运动（后期工人罢工、商人罢市成为主力）",
        "五四运动的目标完全实现了（中国代表最终未在和约上签字，但山东问题未立即解决）",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["巴黎和会", "新民主主义", "工人阶级", "马克思主义", "新文化运动"],
    },
    knownAITraps: [
      "AI 可能将五四运动与新文化运动完全等同",
      "AI 可能忽略工人阶级在五四后期的核心作用",
    ],
  },
  {
    id: "cnhist-004",
    subject: "cn_history",
    courseTitle: "中国近现代史纲要",
    title: "抗日战争",
    content: "七七事变、正面战场与敌后战场、持久战、抗战胜利",
    groundTruth: {
      correctFacts: [
        "全面抗战开始：1937年7月7日（卢沟桥事变/七七事变）",
        "正面战场由国民党军队承担主要作战任务",
        "敌后战场由共产党领导八路军、新四军开展游击战",
        "毛泽东《论持久战》提出战略防御→战略相持→战略反攻三阶段",
        "抗日战争胜利日：1945年8月15日（日本宣布无条件投降）",
        "抗日战争是中国人民第一次取得完全胜利的反侵略战争",
      ],
      commonMisconceptions: [
        "抗日战争只有共产党或只有国民党在打（两个战场都有重要贡献）",
        "南京大屠杀发生在全面抗战开始之前（1937年12月，在七七事变之后）",
        "抗战八年（从七七事变算是8年，从九一八算是14年）",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["remember", "understand", "evaluate"],
      keyTerms: ["七七事变", "正面战场", "敌后战场", "论持久战", "战略相持"],
    },
    knownAITraps: [
      "AI 可能片面强调某一方的抗战贡献",
      "AI 可能混淆14年抗战与8年全面抗战的区分",
    ],
  },
  {
    id: "cnhist-005",
    subject: "cn_history",
    courseTitle: "中国近现代史纲要",
    title: "改革开放",
    content: "十一届三中全会、家庭联产承包责任制、经济特区、社会主义市场经济",
    groundTruth: {
      correctFacts: [
        "1978年十一届三中全会确立改革开放的方针",
        "农村改革：家庭联产承包责任制（安徽凤阳小岗村首创）",
        "1980年设立深圳、珠海、汕头、厦门四个经济特区",
        "1992年邓小平南巡讲话推动改革深化",
        "1992年中共十四大确立社会主义市场经济体制目标",
        "2001年中国加入世界贸易组织（WTO）",
      ],
      commonMisconceptions: [
        "改革开放是突然的政策转向（实际经过了长期的思想解放讨论）",
        "经济特区是完全的资本主义（是社会主义制度下的特殊经济政策区域）",
        "海南是最初的四个经济特区之一（海南是1988年设立的第五个经济特区）",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["十一届三中全会", "家庭联产承包责任制", "经济特区", "南巡讲话", "社会主义市场经济"],
    },
    knownAITraps: [
      "AI 可能将海南列入最初四个经济特区",
      "AI 可能错误描述社会主义市场经济的正式确立时间",
    ],
  },
];

// ─── Subject 8: 大学语文 (Chinese Literature — Chinese-only) ──

const cn_literature: TestKnowledgePoint[] = [
  {
    id: "cnlit-001",
    subject: "cn_literature",
    courseTitle: "大学语文",
    title: "唐诗格律与意象",
    content: "律诗与绝句的格律规则、平仄、对仗、常见意象（月、雁、柳等）",
    groundTruth: {
      correctFacts: [
        "律诗：八句，分首联、颔联、颈联、尾联；颔联和颈联必须对仗",
        "绝句：四句，不要求对仗",
        "平仄规则：一三五不论，二四六分明（简化版）",
        "「月」意象常寄托思乡之情（如李白《静夜思》）",
        "「柳」与「留」谐音，常表送别之意（如王维《送元二使安西》）",
        "「雁」意象常与书信、思归相关（鸿雁传书）",
      ],
      commonMisconceptions: [
        "所有律诗都是五言或七言（也有六言律诗，极少见）",
        "绝句是律诗的一半（虽然形式上四句，但绝句有独立的艺术规律）",
        "「一三五不论」是绝对规则（实际有「孤平」等禁忌需要遵守）",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "apply"],
      keyTerms: ["律诗", "绝句", "平仄", "对仗", "意象"],
    },
    knownAITraps: [
      "AI 可能过度简化平仄规则，不提孤平禁忌",
      "AI 可能混淆近体诗与古体诗的格律要求",
    ],
  },
  {
    id: "cnlit-002",
    subject: "cn_literature",
    courseTitle: "大学语文",
    title: "鲁迅小说的叙事手法",
    content: "《狂人日记》《阿Q正传》的叙事视角、讽刺手法、国民性批判",
    groundTruth: {
      correctFacts: [
        "《狂人日记》是中国现代文学史上第一篇白话小说（1918年）",
        "《狂人日记》采用第一人称内视角，以精神病患者视角揭露封建礼教",
        "「吃人」是对封建礼教压迫的隐喻",
        "《阿Q正传》通过「精神胜利法」讽刺国民劣根性",
        "阿Q是一个典型的文学形象，代表精神麻木的底层民众",
        "鲁迅的创作目的是「揭出病苦，引起疗救的注意」",
      ],
      commonMisconceptions: [
        "《狂人日记》的「狂人」真的是精神病人（是以精神病为叙事策略的象征手法）",
        "鲁迅只写批判性作品（也有《朝花夕拾》等抒情回忆散文）",
        "「精神胜利法」是阿Q个人的问题（鲁迅用它指向更广泛的国民性）",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "analyze", "evaluate"],
      keyTerms: ["白话小说", "叙事视角", "精神胜利法", "国民性批判", "象征手法"],
    },
    knownAITraps: [
      "AI 可能将《狂人日记》简单归类为精神病题材小说",
      "AI 可能不准确描述「精神胜利法」的深层社会含义",
    ],
  },
  {
    id: "cnlit-003",
    subject: "cn_literature",
    courseTitle: "大学语文",
    title: "《红楼梦》的人物塑造",
    content: "贾宝玉、林黛玉、薛宝钗的性格对比，判词与人物命运",
    groundTruth: {
      correctFacts: [
        "贾宝玉：反封建叛逆者，厌恶仕途经济，尊重女性",
        "林黛玉：才华出众，多愁善感，代表真情与个性解放",
        "薛宝钗：温柔敦厚，恪守封建道德规范，代表传统理想女性",
        "金陵十二钗判词暗示了各人物的最终命运",
        "「木石前盟」（宝黛）vs「金玉良缘」（宝钗）是全书核心冲突",
        "作者曹雪芹，前八十回为原作，后四十回一般认为是高鹗续写",
      ],
      commonMisconceptions: [
        "《红楼梦》全书120回都是曹雪芹写的（后40回续作者有争议）",
        "薛宝钗是反面人物（曹雪芹笔下她有正面品质，非简单二元对立）",
        "贾宝玉只是纨绔子弟（他有深刻的反封建思想和人文关怀）",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "analyze", "evaluate"],
      keyTerms: ["金陵十二钗", "木石前盟", "金玉良缘", "叛逆", "封建礼教"],
    },
    knownAITraps: [
      "AI 可能简单化贾宝玉为「不学无术」",
      "AI 可能将薛宝钗塑造为纯反面角色",
    ],
  },
  {
    id: "cnlit-004",
    subject: "cn_literature",
    courseTitle: "大学语文",
    title: "先秦诸子思想",
    content: "儒家（孔子、孟子）、道家（老子、庄子）、法家（韩非子）核心主张对比",
    groundTruth: {
      correctFacts: [
        "孔子核心思想：仁、礼、中庸；强调君子人格和社会等级秩序",
        "孟子主张性善论、仁政、民贵君轻",
        "老子：道法自然、无为而治、祸福相依",
        "庄子：逍遥游、齐物论、追求精神自由",
        "韩非子：法家集大成者，主张以法治国、术势结合",
        "百家争鸣发生在春秋战国时期（约公元前770-前221年）",
      ],
      commonMisconceptions: [
        "道家的「无为」是什么都不做（是不妄为，顺应自然规律而为）",
        "法家只讲严刑峻法（还强调「术」和「势」的综合运用）",
        "孔子反对社会变革（他主张恢复周礼，但也有革新思想）",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["仁", "道法自然", "无为而治", "性善论", "法术势"],
    },
    knownAITraps: [
      "AI 可能过度简化「无为」为消极不作为",
      "AI 可能混淆孔子和孟子的具体主张",
    ],
  },
  {
    id: "cnlit-005",
    subject: "cn_literature",
    courseTitle: "大学语文",
    title: "宋词流派与风格",
    content: "豪放派（苏轼、辛弃疾）与婉约派（柳永、李清照）的风格对比",
    groundTruth: {
      correctFacts: [
        "豪放派代表：苏轼、辛弃疾；题材广阔，意境开阔",
        "婉约派代表：柳永、李清照；题材以爱情离别为主，语言精致",
        "苏轼《念奴娇·赤壁怀古》是豪放词的典范",
        "李清照被誉为「千古第一才女」，早期词清新婉丽，晚期词悲凉沉郁",
        "辛弃疾：南宋爱国词人，词中多抒发报国壮志和壮志难酬之悲",
        "词牌名规定了词的格律（如《水调歌头》《声声慢》），不等于词的内容",
      ],
      commonMisconceptions: [
        "苏轼只写豪放词（他也有婉约词如《江城子·十年生死两茫茫》）",
        "婉约派 = 女性化/低级（婉约词有高度的艺术成就）",
        "词牌名就是词的标题（词牌规定格式，题目另取或不取）",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["remember", "understand", "analyze"],
      keyTerms: ["豪放派", "婉约派", "词牌", "苏轼", "李清照", "辛弃疾"],
    },
    knownAITraps: [
      "AI 可能将苏轼简单归类为纯豪放派",
      "AI 可能混淆词牌名和词的标题",
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
  ...cn_history,
  ...cn_literature,
];

export const TEST_SUBJECTS: Record<Subject, TestKnowledgePoint[]> = {
  calculus,
  physics,
  cs,
  economics,
  psychology,
  biology,
  cn_history,
  cn_literature,
};

export const SUBJECT_LABELS: Record<Subject, string> = {
  calculus: "Calculus II (微积分)",
  physics: "General Physics (普通物理)",
  cs: "Data Structures & Algorithms (数据结构)",
  economics: "Microeconomics (微观经济学)",
  psychology: "Cognitive Psychology (认知心理学)",
  biology: "Molecular Biology (分子生物学)",
  cn_history: "中国近现代史纲要",
  cn_literature: "大学语文",
};
