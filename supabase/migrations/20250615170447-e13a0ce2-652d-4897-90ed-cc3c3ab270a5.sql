
-- Insérer les compétences en français et en anglais (chaque compétence aura deux entrées, une par langue)
insert into public.skills (name, level)
values
  -- Pentest & cybersécurité (FR)
  ('Pentest web (OWASP, XSS, SQLi…)', 'Avancé'),
  ('Pentest réseau (scans, exploitation de vulnérabilités)', 'Avancé'),
  ('Audit de configuration (serveur, cloud, IoT)', 'Intermédiaire'),
  ('Sécurité offensive (Red Team, exploitation)', 'Avancé'),
  ('Rédaction de rapports d’audit et de plan de remédiation', 'Intermédiaire'),
  ('Veille et surveillance des vulnérabilités', 'Intermédiaire'),
  ('Reverse engineering & analyse de protocoles réseaux', 'Intermédiaire'),
  ('Sécurité des applications Python', 'Intermédiaire'),
  ('Tests d’intrusion sur IoT et réseaux industriels', 'Débutant'),
  -- Programmation/Scripting (FR)
  ('Développement d’outils Python pour la cybersécurité', 'Avancé'),
  ('Scripting Bash & PowerShell', 'Intermédiaire'),
  ('Analyse automatisée de logs', 'Intermédiaire'),
  ('Développement de scanners de vulnérabilités', 'Intermédiaire'),
  ('Utilisation de frameworks Python (Scapy, Requests, Flask)', 'Avancé'),
  ('Création de bots/brute force en Python', 'Intermédiaire'),
  ('Fuzzing et outils de sécurité personnalisés', 'Débutant'),
  -- Réseau/Infra (FR)
  ('Diagnostic et sécurisation des infrastructures réseau', 'Avancé'),
  ('Analyse de trafic (Wireshark, tcpdump)', 'Intermédiaire'),
  ('Configuration VPN, Firewall, IDS/IPS', 'Intermédiaire'),
  ('Mise en place de labs de pentest/CTF', 'Intermédiaire'),
  -- Sensibilisation/Conseil (FR)
  ('Animation d’ateliers et formations cyber', 'Intermédiaire'),
  ('Sensibilisation aux bonnes pratiques', 'Intermédiaire'),

  -- Pentest & Cybersecurity (EN)
  ('Web pentest (OWASP, XSS, SQLi, ...)', 'Advanced'),
  ('Network pentest (scanning, vulnerability exploitation)', 'Advanced'),
  ('Configuration audit (servers, cloud, IoT)', 'Intermediate'),
  ('Offensive security (Red Team, exploitation)', 'Advanced'),
  ('Report writing & remediation plan', 'Intermediate'),
  ('Vulnerability monitoring & threat intelligence', 'Intermediate'),
  ('Reverse engineering & network protocol analysis', 'Intermediate'),
  ('Python application security', 'Intermediate'),
  ('IoT & industrial network pentesting', 'Beginner'),
  -- Scripting/Programming (EN)
  ('Python tool development for cybersecurity', 'Advanced'),
  ('Bash & PowerShell scripting', 'Intermediate'),
  ('Automated log analysis', 'Intermediate'),
  ('Vulnerability scanner development', 'Intermediate'),
  ('Python frameworks (Scapy, Requests, Flask)', 'Advanced'),
  ('Bot/brute force development in Python', 'Intermediate'),
  ('Fuzzing & custom security tooling', 'Beginner'),
  -- Network/Infra (EN)
  ('Network infrastructure diagnosis & hardening', 'Advanced'),
  ('Traffic analysis (Wireshark, tcpdump)', 'Intermediate'),
  ('VPN, Firewall, IDS/IPS configuration', 'Intermediate'),
  ('Setting up pentest/CTF labs', 'Intermediate'),
  -- Security awareness/Consulting (EN)
  ('Cybersecurity workshops & training facilitation', 'Intermediate'),
  ('Security awareness for best practices', 'Intermediate')
;
