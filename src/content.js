// Everything the visitor can read. Edit freely: `todo` marks shelves that still need Deby's real answers.
const LI = ['LinkedIn', 'https://www.linkedin.com/in/dangelina1/'];
const GH = ['GitHub', 'https://github.com/debdeb18'];
const repo = (n, label) => [label || n, `https://github.com/debdeb18/${n}`];

export const CONTENT = {
  // ---------- terminal ----------
  welcome: {
    kicker: 'Notice board', title: 'You have arrived Somewhere',
    body: `<p>Hi, I'm <b>Deby Angelina</b>, a backend / platform software engineer in Seoul. This platform is my portfolio.</p>
      <p>Three lines leave from here. Sit on the chair, pick a ticket, and when the train passes, the air behind it cracks open.</p>
      <ul><li><b>Home among the stars</b>: who I am</li><li><b>The Office</b>: my work, projects and how I work</li><li><b>The Night Market</b>: everything outside work</li></ul>
      <p class="hint">In a hurry? The buttons in the top-right corner skip the train.</p>`,
  },
  contact: {
    kicker: 'Say hi', title: 'Let’s build something',
    body: `<p>I like small teams, hard bugs, and systems that people actually depend on. If that sounds like your kind of project, or you just want to talk shop (or games), reach out.</p>`,
    links: [LI, GH],
  },

  // ---------- home ----------
  about: {
    kicker: 'Home · memory wall', title: 'Deby Angelina · 안젤리나 데비',
    body: `<p>I grew up in <b>Semarang, Indonesia</b>, moved to Korea for university, and stayed to build things. Today I'm a backend / platform engineer in <b>Seoul</b>.</p>
      <p>I enjoy debugging and untangling complex problems, especially that proud, slightly ecstatic moment when one finally gives in. I'm resourceful by nature: I make the most of what's around me, whether that's people, knowledge or technology.</p>
      <blockquote>Winner is your nature, so don't worry about it. Setting your focus on what's naturally yours will just mess up your tempo.</blockquote>`,
  },
  journey: {
    kicker: 'Home · the globe', title: 'Semarang → Seoul',
    body: `<p>Two cities, three languages.</p>
      <ul><li><b>Indonesian</b>: native</li><li><b>English</b>: professional</li><li><b>Korean</b>: professional</li></ul>
      <p>Working across all three means I end up as the bridge fairly often: between teammates, customers, and field sites.</p>`,
  },
  education: {
    kicker: 'Home · bookshelf', title: 'Dankook University',
    body: `<p><b>B.S. in Mobile Systems Engineering</b><br>Jukjeon Campus · Sep 2018 – Aug 2022</p>
      <p>Where I met C, computer architecture (I built MIPS simulators for class), Android, and the habit of reading things byte by byte.</p>`,
  },
  art: {
    kicker: 'Home · easel', title: 'Art stuff',
    body: `<p>When I'm not coding or racking my brain, I'm usually making something with my hands.</p>`,
    todo: 'Deby: what do you draw / make? Send a few pieces and they go on this easel and in the market gallery.',
  },
  play: {
    kicker: 'Home · the couch corner', title: 'The virtual world',
    body: `<p>The other place you'll find me after hours: online games.</p>`,
    todo: 'Deby: which games, which roles, any proud ranks?',
  },
  dream: {
    kicker: 'Home · telescope', title: 'Why the house is in space',
    body: `<p>This is the fantasy goal: a studio out here, where the window is all stars and the commute is zero.</p>
      <p>Until then, I keep building the earthbound version one service at a time.</p>`,
  },

  // ---------- office ----------
  naonworks: {
    kicker: 'Office · reception', title: 'Naonworks · Edge Computing Platform Developer',
    body: `<p><b>Jul 2022 – present · Seoul</b> (full-time from Oct 2022)</p>
      <p>Four years designing, building and operating microservice data platforms. I'm the original author of <b>14+ production services</b> in C#/.NET across two platforms: an edge-computing core platform and a traffic-signal integration gateway.</p>
      <ul><li>End-to-end data pipeline: field devices (TCP / serial / Modbus) → transformation and storage → cloud (Azure, AWS)</li>
      <li>Messaging layer on RabbitMQ, Kafka and MQTT</li>
      <li>Incident response on live systems in public transport, water utilities and logistics</li>
      <li>Several customer projects delivered end to end as the sole engineer</li></ul>
      <p class="hint">Dev room = how it's built. Archive = the project files. Meeting room = how I work.</p>`,
    links: [LI],
  },
  skills: {
    kicker: 'Office · dev room', title: 'What’s on my desk',
    body: `<dl><dt>Languages</dt><dd>C# (.NET 8), C (embedded, PowerPC cross-compilation), SQL</dd>
      <dt>Backend</dt><dd>ASP.NET Core, IHostedService microservices, REST API design, Blazor, EF Core, Serilog</dd>
      <dt>Messaging</dt><dd>RabbitMQ (AMQP), Kafka, MQTT, Modbus TCP/RTU, custom binary protocols</dd>
      <dt>Databases</dt><dd>PostgreSQL, MySQL/MariaDB, MSSQL, Oracle, SQLite, MongoDB, InfluxDB 2, OpenSearch</dd>
      <dt>Cloud / infra</dt><dd>Azure IoT Hub / Event Hubs, AWS (KMS, CloudWatch), Docker, systemd, Linux</dd>
      <dt>Security</dt><dd>mTLS, JWT, TPM 2.0, KMS credential encryption, checksum-based device auth</dd></dl>`,
  },
  core: {
    kicker: 'Office · server rack', title: 'Edge Computing Core Platform',
    body: `<p><b>2022 – present</b> · C# .NET 8 · MQTT · RabbitMQ · Kafka · InfluxDB 2 · OpenSearch · PostgreSQL · MongoDB</p>
      <p>Original author of all core services:</p>
      <ul><li><b>Data ingestion</b>: a generic packet-parser engine that decodes TCP/serial binary streams purely from DB-driven configuration</li>
      <li><b>ETL engine</b>: JSONPath rule engine that transforms raw MQTT data and re-publishes to Kafka, InfluxDB and RabbitMQ, with no code changes</li>
      <li><b>Three persistence services</b>: InfluxDB/MongoDB, RabbitMQ (Sparkplug-B), Azure IoT Hub / Event Hubs</li>
      <li><b>Event processing</b>: connection and bucket/index lifecycle hub, with mTLS + JWT auth and self-healing retention policies</li>
      <li><b>Modbus server</b>: exposes MQTT data to legacy PLC/SCADA masters, with atomic multi-coil writes</li></ul>`,
  },
  pipeline: {
    kicker: 'Office · whiteboard', title: 'The pipeline, on one board',
    body: `<p class="flow">field devices <i>TCP · serial · Modbus</i><br>↓<br>ingestion + packet parsing<br>↓<br>MQTT / RabbitMQ / Kafka<br>↓<br>ETL rule engine <i>JSONPath</i><br>↓<br>InfluxDB · OpenSearch · PostgreSQL · MongoDB<br>↓<br>cloud <i>Azure IoT Hub / Event Hubs · AWS</i></p>
      <p>A continuous stream of events from thousands of devices: validated, transformed, routed, persisted, forwarded. I designed the architecture and own every box on this board.</p>`,
  },
  traffic: {
    kicker: 'Archive · cabinet 1', title: 'Traffic Signal Integration Gateway',
    body: `<p><b>2023 – present</b> · in production for a public road-traffic authority · RabbitMQ · AMQP · REST · TCP binary protocols</p>
      <ul><li><b>Authentication service</b>: device OTP hub on RabbitMQ auth webhooks, checksum-based verification, backward compatible with legacy firmware</li>
      <li><b>State router</b>: a real-time in-memory digital twin of every intersection (phase, timing, detection), exposed over REST</li>
      <li><b>External bridge</b>: AMQP bridge to multiple road-control systems with state-machine connection management</li>
      <li><b>Controller service</b>: TCP sessions with signal controllers, DB-driven variable-length binary parser, sunrise/sunset-based brightness and volume control</li></ul>`,
  },
  logistics: {
    kicker: 'Archive · cabinet 2', title: 'Embedded Logistics Daemon',
    body: `<p><b>2023 – 2024</b> · C · PowerPC cross-compilation · epoll · Oracle / PostgreSQL · Docker</p>
      <p>A C daemon for a PowerPC embedded target: epoll-based non-blocking TCP sessions, STX/ETX framing, DB-driven routing rules and message relay.</p>
      <p>Deployed to multiple customer sites, with a Docker-based build and release process I set up.</p>`,
  },
  v2x: {
    kicker: 'Archive · cabinet 3', title: 'V2X and Water-Utility Extensions',
    body: `<p><b>2023 – 2024</b> · C# · PostgreSQL / MySQL · AWS KMS</p>
      <ul><li><b>V2X</b>: vehicle-to-infrastructure service managing several roadside device types, with a built-in simulator mode so everything can be tested without hardware</li>
      <li><b>Water utility</b>: flow, pressure and quality sensor data mapped into PostgreSQL/MySQL, with KMS-encrypted credentials</li></ul>`,
  },
  tools: {
    kicker: 'Archive · cabinet 4', title: 'Cloud Ops, Hardware Control, Dev Tools',
    body: `<p><b>2023 – present</b> · C# · Blazor · statsd · CloudWatch · GPIO / I2C</p>
      <ul><li>A RabbitMQ load-test simulator: up to <b>7,500 concurrent connections</b></li>
      <li>A CLI for binary protocol encode/decode and TCP/UDP testing</li>
      <li>Container-level resource telemetry to CloudWatch via statsd</li>
      <li>REST API + Blazor app for I2C temperature/humidity monitoring and GPIO fan/heater control, for an autonomous-driving research deployment</li></ul>`,
  },
  ethic: {
    kicker: 'Office · meeting room', title: 'How I work',
    body: `<ul><li><b>Own the system, not the ticket.</b> On a small team I've owned every layer: architecture, implementation, deployment, and the on-call debugging when a live site calls.</li>
      <li><b>Configuration over code.</b> If a customer will want it changed, it should be a rule, not a release.</li>
      <li><b>Careful by default.</b> Concurrency, failure modes and security are part of the design, not the retro.</li>
      <li><b>Read the bytes.</b> When the logs run out, I read protocol traffic byte by byte.</li>
      <li><b>Three languages, one conversation.</b> Korean, English, Indonesian, with customers and on site.</li></ul>`,
  },
  fixes: {
    kicker: 'Office · incident board', title: 'The unglamorous fixes',
    body: `<p>The ones I'm proudest of:</p>
      <ul><li>A <b>dispose-race between threads</b> that crashed a production TCP server</li>
      <li>A Modbus write path that <b>silently corrupted register values</b> through an integer cast</li>
      <li>A multi-coil write made <b>atomic</b>, so a partial failure can't corrupt PLC state</li>
      <li>A <b>credential-handling defect</b>, closed quietly and quickly</li></ul>
      <p>Finding these in systems people depend on is what made me careful.</p>`,
  },
  fuel: {
    kicker: 'Office · pantry', title: 'Fuel',
    body: `<p>Every office runs on something.</p>`,
    todo: 'Deby: coffee order? snack of choice? what does a good work day look like?',
  },

  // ---------- market ----------
  games: {
    kicker: 'Night market · PLAY', title: 'The game stall',
    body: `<p>Online games are where I go when I'm not coding. I've also shipped one of my own: <b>Sloppy</b>, an Android game in Java + JNI.</p>`,
    links: [repo('sloppy-game', 'Sloppy')],
    todo: 'Deby: favourite games and what you main.',
  },
  gallery: {
    kicker: 'Night market · ART', title: 'The art stall',
    body: `<p>Prints, sketches and whatever I've been making lately.</p>`,
    todo: 'Gallery opens when the pictures arrive.',
  },
  words: {
    kicker: 'Night market · WORDS', title: 'Thoughts and writing',
    body: `<p>A zine rack for notes, opinions and things I figured out the hard way.</p>`,
    todo: 'No zines printed yet. Deby: any writing or topics you want here?',
  },
  side: {
    kicker: 'Night market · SIDE QUESTS', title: 'Side projects',
    body: `<p>Things built for the fun of it (and a few for class):</p>
      <ul><li><b>Compareit</b>: a shopping comparison app in React</li><li><b>Sloppy</b>: an Android game in Java + JNI</li><li><b>Vending Machine</b>: an OOP exercise in C++ (it lives on at the terminal)</li></ul>`,
    links: [repo('compareit-frontend-react', 'Compareit'), repo('sloppy-game', 'Sloppy'), repo('vending-macine-OOP-project', 'Vending Machine')],
  },
  lab: {
    kicker: 'Night market · THE LAB', title: 'Silly experiments',
    body: `<p>Too unpolished for the office, too fun to throw away. Currently on the shelf: CPUs written in C.</p>
      <ul><li>MIPS single-cycle simulator</li><li>MIPS pipeline simulator</li><li>A simple calculator machine</li></ul>
      <p>Also: this whole 3D world counts.</p>`,
    links: [repo('MIPS-single-cycle-implementation-in-C', 'Single cycle'), repo('MIPS-pipeline-implementation-in-C', 'Pipeline'), repo('simple-calculator', 'Simple calc')],
  },
  food: {
    kicker: 'Night market · EATS', title: 'The food truck',
    body: `<p>Tonight's menu is still being written.</p>`,
    todo: 'Deby: favourite foods? Indonesian comfort dishes, Korean go-tos, things you cook?',
  },
  goods: {
    kicker: 'Night market · GOODS', title: 'Shop of things I like',
    body: `<p>Shelves for the stuff I collect, recommend, or can't stop talking about.</p>`,
    todo: 'Deby: what goes on the shelves? Music, shows, books, gadgets, collections?',
  },
};
