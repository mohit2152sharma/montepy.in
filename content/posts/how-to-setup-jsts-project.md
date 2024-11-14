---
title: How to set up a JavaScript/TypeScript project
date: 2024-11-14T17:27:43+05:30
draft: false
tags: ["how-to", "javascript", "typescript"]
canonicalUrl: https://montepy.in/posts/how-to-setup-jsts-project
ShowBreadCrumbs: true
categories: ["how-to"]
---

## Running a Javascript file

Suppose you have a javascript file that you want to run from the command line.

1. Install `node` or `deno`
2. Run the file with `node <filepath.js>` or `deno <filepath.js>` or `deno run <filepath.js>`

## Running a TypeScript file

Suppose you have a typescript file that you want to run from the command line.

1. Install `node`. `npm` comes bundled with `node`.
2. Install the typescript compiler with `npm install -g typescript`. Note that this will install the latest version of typescript compiler globally.
3. Compile the file with `tsc <filepath.ts>`
4. Run the file with `node <comiled-filepath.js>`
5. Alternatively, you can install the `ts-node` package with `npm install -g ts-node`. This will install the latest version of `ts-node` globally. `ts-node` compiles the file on the file and executes it. `ts-node <filepath.ts>`

## Running a Javascript project

1. The project directory must have a `package.json` file. This file is used by `npm` and can also be used to define additional information if you plan to publish the module to `npm` registry.
2. Install the dependencies mentioned in the `package.json` file with `npm install`, [more details about `package.json`](https://docs.npmjs.com/cli/v10/configuring-npm/package-json)
3. The `package.json` file have a `scripts` section, this defines the commands that can be run with `npm run <command>`. In this section, you can define commands like `start: node index.js; test: jest .`, then if you run `npm run test` it will run the tests.
4. Note, `npm` defines three commands which can be run without using the `run` command, `npm start`, `npm test` and `npm stop`. The `start` command defaults to using `index.js` file
5. The `package.json` file has a `main` field, this is the file that is executed when you import the package in another file.
6. By default, `npm` treats the imports as CommonJS modules, if you are using ES modules, you need to add the `type` key in your `package.json` with value `module`. Then all files must use `import/export` syntax.

```json5
{
  name: "my-package",
  version: "1.0.0",
  main: "index.js",
  scripts: {
    start: "node index.js",
    test: "jest .",
  },
  type: "module",
  dependencies: {
    jest: "^27.5.1",
  },
}
```

## Running a TypeScript project

### Using `ts-node`

> [!NOTE]
> You can avoid using `ts-node` and use `tsx` which supports TypeScript out of the box. No need to add additional support for esm modules

1. In addition to the steps mentioned above for Javascript, the project directory must also have a `tsconfig.json` file. This file is used by `typescript` compiler to compile the files. Note you would still need to install `typescript` (or `ts-node`) 2. The `tsconfig.json` file has a `compilerOptions` section, this defines the options for the compiler. In this section, you can define the `target` option, which tells which version of ECMAScript to compile to (use `ESNext` for latest ECMAScript standard). There are more options available for `tsconfig.json`, [reference](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)

```json5
{
  compilerOptions: {
    target: "ESNext", // which version of ECMAScript to compile to
    module: "ESNext", // which module system to compile to (ECMAScript modules or CommonJS)
    moduleResolution: "node", // resolve modules using Node.js style e.g. looking in `node_modules` folder
    strict: true, // enable strict type checking
    esModuleInterop: true, // enable interoperability with ES modules and CommonJS modules
    skipLibCheck: true, // skip type checking of all declaration files (*.d.ts) these files might be used for third party modules types
  },
  include: ["src/**/*.ts"], // which files to include in compilation
  exclude: ["node_modules", "dist"], // which files to exclude from compilation
  outDir: "dist", // where to place the compiled files
  // If you are using ECMAScript moduels and ts-node, then add the following
  "ts-node": {
    esm: true,
  },
}
```

3. In your `package.json` file, modify the `scripts` section to include compilation commands for typescript files.

```json5
{
  scripts: {
    start: "node dist/index.js",
    test: "jest .",
    build: "tsc",
    dev: "ts-node src/index.ts",
    // dev: "ts-node --esm src/index.ts" // if you are using ES modules
  },
}
```
