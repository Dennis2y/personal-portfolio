// Simple DennisChat brain: keyword-based replies
function getDennisChatReply(rawInput) {
  if (!rawInput || typeof rawInput !== "string") {
    return "I didn’t catch that. Could you please repeat your question?";
  }

  const msg = rawInput.trim().toLowerCase();

  // --- GREETINGS ---

  // English: hello, hi
  if (msg === "hello" || msg === "hi" || msg.startsWith("hello ") || msg.startsWith("hi ")) {
    return (
      "Hello! 👋 How can I help you today?\n" +
      "You can ask me about Dennis, Denarixx, his projects, or general questions about creativity and AI."
    );
  }

  // Spanish: hola
  if (msg === "hola" || msg.startsWith("hola ")) {
    return (
      "¡Hola! 👋 ¿Cómo puedo ayudarte hoy?\n" +
      "Puedes preguntarme sobre Dennis, sus proyectos, Denarixx o temas generales de creatividad e inteligencia artificial."
    );
  }

  // German: hallo
  if (msg === "hallo" || msg.startsWith("hallo ")) {
    return (
      "Hallo! 👋 Wie kann ich dir heute helfen?\n" +
      "Du kannst mir Fragen zu Dennis Charles, seinen Projekten, Denarixx oder zu kreativen Themen mit KI stellen."
    );
  }

  // Arabic: صباح الخير
  if (msg.includes("صباح الخير")) {
    return (
      "صباح النور! 🌞 كيف يمكنني مساعدتك اليوم؟\n" +
      "يمكنك طرح أسئلة حول دينيس تشارلز، مشروع Denarixx، أو مواضيع عامة عن الإبداع والذكاء الاصطناعي."
    );
  }

  // Spanish: buenos días
  if (msg.includes("buenos dias") || msg.includes("buenos días")) {
    return (
      "¡Buenos días! 🌞 ¿En qué puedo ayudarte hoy?\n" +
      "Si quieres saber más sobre Dennis, Denarixx o sus proyectos creativos con IA, pregúntame lo que quieras."
    );
  }

  // French: bonjour
  if (msg.startsWith("bonjour")) {
    return (
      "Bonjour ! 👋 Comment puis-je t’aider aujourd’hui ?\n" +
      "Tu peux me poser des questions sur Dennis, Denarixx, ses projets ou des sujets liés à la créativité et à l’IA."
    );
  }

  // --- WHO IS DENNIS? / QUI EST / WER IST / ¿QUIÉN ES / من هو ---

  // German: Wer ist Dennis Charles?
  if (msg.includes("wer ist dennis charles")) {
    return (
      "Dennis Charles, auch bekannt als „Denarixx“, ist ein AI-Engineer und kreativer Digital Creator mit Sitz in Deutschland.\n" +
      "Er arbeitet an Projekten rund um KI, Automatisierung, kreative Inhalte und seinem eigenen Brand Denarixx – von Smartphones bis hin zu Automotive- und Digital-Lösungen.\n" +
      "Wenn du mehr über seine Projekte oder Vision erfahren möchtest, frag einfach nach einem bestimmten Bereich (z.B. Auto-Projekt, Smartphone, AI-Videotools)."
    );
  }

  // German: Wer ist Dennis ?
  if (msg.includes("wer ist dennis")) {
    return (
      "Dennis ist der Kopf hinter der Marke „Denarixx“.\n" +
      "Er kombiniert KI, Softwareentwicklung und Design, um neue Produkte und Services zu entwickeln – zum Beispiel AI-gestützte Websites, Video-Automatisierung und Konzeptfahrzeuge.\n" +
      "Wenn du etwas Konkretes über ihn wissen willst (z.B. Werdegang, Projekte, Mindset), sag mir einfach, was dich interessiert."
    );
  }

  // English: Who is Dennis Charles?
  if (msg.includes("who is dennis charles")) {
    return (
      "Dennis Charles, also known as “Denarixx”, is an AI engineer and creative founder based in Germany.\n" +
      "He works on several ambitious projects that combine artificial intelligence, design, and digital products — including Denarixx smartphones, automotive concepts, AI video tools, and digital services.\n" +
      "If you’d like, I can tell you more about his background, his projects, or his long-term vision."
    );
  }

  // French: Qui est Dennis Charles ?
  if (msg.includes("qui est dennis charles")) {
    return (
      "Dennis Charles, aussi connu sous le nom de « Denarixx », est un ingénieur en IA et créateur digital basé en Allemagne.\n" +
      "Il développe des projets qui mélangent intelligence artificielle, design et produits créatifs — comme des concepts de smartphones, d’automobile et des outils vidéo pilotés par l’IA.\n" +
      "Si tu veux, je peux te raconter son parcours, ses projets actuels ou sa vision pour Denarixx."
    );
  }

  // Spanish: ¿Quién es Dennis Charles?
  if (msg.includes("quién es dennis charles") || msg.includes("quien es dennis charles")) {
    return (
      "Dennis Charles, también conocido como «Denarixx», es un ingeniero de IA y creador digital que vive en Alemania.\n" +
      "Trabaja en varios proyectos que combinan inteligencia artificial, diseño y productos creativos: desde conceptos de smartphones y automóviles hasta herramientas de vídeo automatizadas y servicios digitales.\n" +
      "Si quieres saber más sobre su historia, sus proyectos o su visión con Denarixx, dime qué te interesa."
    );
  }

  // Arabic: من هو دينيس تشارلز؟
  if (msg.includes("من هو دينيس تشارلز")) {
    return (
      "دينيس تشارلز، المعروف أيضًا باسم «ديناريكس» (Denarixx)، هو مهندس ذكاء اصطناعي ومبدع رقمي يعيش في ألمانيا.\n" +
      "يعمل على مشاريع تجمع بين الذكاء الاصطناعي والتصميم والمنتجات الإبداعية، مثل هواتف ذكية مفهومية، مشاريع سيارات، وأدوات فيديو وآليات رقمية قائمة على الـ AI.\n" +
      "إذا أحببت، يمكنني أن أشرح لك أكثر عن قصته، مشاريعه أو رؤيته المستقبلية."
    );
  }

  // --- JOB QUESTION (DE): Welche Art von Job passt am besten... ---

  if (msg.includes("welche art von job passt am besten zu dennis als ai-engineer")) {
    return (
      "Als AI-Engineer passt zu Dennis besonders gut ein Job, in dem er:\n" +
      "\n" +
      "- mit kreativen KI-Lösungen arbeitet (z.B. Generative AI, Automatisierung, Chatbots, Video-/Content-Automation),\n" +
      "- Prototypen und Produkte baut (z.B. AI-Features für Apps, Smartphone- oder Automotive-Projekte),\n" +
      "- und seine eigenen Ideen und Marken wie Denarixx weiterentwickeln kann.\n" +
      "\n" +
      "Ideal wären Rollen wie:\n" +
      "- AI-Engineer oder Machine-Learning-Engineer in einem innovativen Tech-Unternehmen,\n" +
      "- Creative Technologist / AI Product Developer,\n" +
      "- oder eine Position in einem Startup, in dem er an End-to-End-Lösungen arbeitet (von Idee über Prototyp bis Launch).\n" +
      "\n" +
      "Grundsätzlich passt alles gut zu ihm, wo KI + Kreativität + eigene Verantwortung zusammenkommen."
    );
  }

  // --- DEFAULT FALLBACK ---

  return (
    "I’m DennisChat 🤖. I can answer questions about Dennis, Denarixx, this site, and some high-level AI/creative topics.\n" +
    "Try asking things like:\n" +
    "- \"Who is Dennis Charles?\"\n" +
    "- \"Tell me about the Denarixx car project\"\n" +
    "- \"What kind of job fits Dennis as an AI engineer?\""
  );
}
