import { existsSync, readFileSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const manifestPath = path.join(root, ".claude-plugin", "plugin.json");
const packagePath = path.join(root, "package.json");

function fail(message) {
  console.error(message);
  process.exitCode = 1;
}

function readJson(filePath, label) {
  try {
    return JSON.parse(readFileSync(filePath, "utf8"));
  } catch (error) {
    fail(`invalid ${label}: ${error.message}`);
    return undefined;
  }
}

function packageFileEntryCovers(files, relativePath) {
  return files.some((entry) => {
    if (typeof entry !== "string") {
      return false;
    }

    const normalized = entry.replace(/^\.\//, "").replace(/\/$/, "");
    return normalized === relativePath || normalized === `${relativePath}/**`;
  });
}

let packageFiles;

if (existsSync(packagePath)) {
  const packageJson = readJson(packagePath, "package.json");

  if (packageJson) {
    if (!Array.isArray(packageJson.files)) {
      fail("package.json must have a files array");
    } else {
      packageFiles = packageJson.files;

      if (packageFiles.some((entry) => typeof entry !== "string")) {
        fail("package.json files entries must be strings");
      }

      if (!packageFileEntryCovers(packageFiles, ".claude-plugin")) {
        fail("package.json files must include .claude-plugin");
      }
    }
  }
}

if (!existsSync(manifestPath)) {
  fail("missing .claude-plugin/plugin.json");
} else {
  const manifest = readJson(manifestPath, "plugin.json");

  if (manifest) {
    if (typeof manifest.name !== "string" || manifest.name.length === 0) {
      fail("plugin.json must have a non-empty string name");
    }

    if (!Array.isArray(manifest.skills) || manifest.skills.length === 0) {
      fail("plugin.json must have a non-empty skills array");
    }

    for (const skillPath of manifest.skills ?? []) {
      if (typeof skillPath !== "string" || !skillPath.startsWith("./")) {
        fail(`invalid skill path: ${skillPath}`);
        continue;
      }

      const packageSkillPath = skillPath.replace(/^\.\//, "").replace(/\/$/, "");

      if (packageFiles && !packageFileEntryCovers(packageFiles, packageSkillPath)) {
        fail(`package.json files must include manifest skill: ${packageSkillPath}`);
      }

      const absoluteSkillPath = path.join(root, skillPath);
      const skillFilePath = path.join(absoluteSkillPath, "SKILL.md");

      if (!existsSync(absoluteSkillPath)) {
        fail(`missing skill directory: ${skillPath}`);
        continue;
      }

      if (!existsSync(skillFilePath)) {
        fail(`missing SKILL.md for skill: ${skillPath}`);
        continue;
      }

      const skillFile = readFileSync(skillFilePath, "utf8");
      const frontmatter = skillFile.match(/^---\n([\s\S]*?)\n---/);

      if (!frontmatter) {
        fail(`SKILL.md missing YAML frontmatter: ${skillPath}`);
        continue;
      }

      const name = frontmatter[1].match(/^name:\s*([a-z0-9-]+)\s*$/m);

      if (!name) {
        fail(`SKILL.md frontmatter must include a valid name`);
      } else if (name[1] !== path.basename(skillPath)) {
        fail(`SKILL.md name must match its directory: ${skillPath}`);
      }

      if (!/^description:\s*\S/m.test(frontmatter[1])) {
        fail(`SKILL.md frontmatter must include a non-empty description`);
      }
    }
  }
}

if (process.exitCode) {
  process.exit();
}

console.log("OK: plugin manifest and skill frontmatter are valid");
