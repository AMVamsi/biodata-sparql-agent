# Biodata SPARQL Agent

[![Deploy to GitHub pages](https://github.com/AMVamsi/biodata-sparql-agent/actions/workflows/deploy.yml/badge.svg)](https://github.com/AMVamsi/biodata-sparql-agent/actions/workflows/deploy.yml)
[![Python CI](https://github.com/AMVamsi/biodata-sparql-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/AMVamsi/biodata-sparql-agent/actions/workflows/ci.yml)

A RAG chatbot that converts natural language questions into SPARQL queries, executes them against live biological databases (UniProt, Bgee, OMA Browser), and summarises the results — all via a Chainlit chat UI.

- Practical slides: https://AMVamsi.github.io/biodata-sparql-agent

## 🛠 Slides development

> Prerequisites: [NodeJS](https://nodejs.org/en/download)

Install dependencies:

```sh
npm i
```

Deploy in development:

```sh
npm run dev
```

Build for production in the `dist` folder:

```sh
npm run build
```

Check production build:

```sh
npm run preview
```

Upgrade dependencies in `package.json`:

```sh
npm run upgrade
```

## 🎯 Deployment

This slide deck is set up to automatically deploy to GitHub Pages via GitHub Actions.
