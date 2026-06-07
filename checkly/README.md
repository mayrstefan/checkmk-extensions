# Checkly special agent

Special agent to query the ChecklyHQ API and retrieve all Checkly services as Checkmk services

## Setup
- Create a dummy host, e.g. app.checklyhq.com
- Create Checkly rule and bind it to that explicit host
- Run Service discovery on that host
