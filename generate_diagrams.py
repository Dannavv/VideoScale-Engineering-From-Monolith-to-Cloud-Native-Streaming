import os
import re
import subprocess
from pathlib import Path

# Resolve directories based on the location of this script
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = ROOT_DIR / "assets" / "diagrams"

def generate_architecture_images():
    """Scans all Markdown files for Mermaid diagrams and generates images."""
    print(f"🔍 Scanning {ROOT_DIR} for Markdown files...")
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    md_files = list(ROOT_DIR.rglob("*.md"))
    # Regex to find all mermaid code blocks
    mermaid_regex = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
    
    diagram_count = 0

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        matches = mermaid_regex.findall(content)
        
        for i, match in enumerate(matches):
            diagram_count += 1
            # Create a predictable name based on the markdown file's folder/name
            diagram_name = f"{md_file.parent.name}_{md_file.stem}_{i+1}"
            mmd_path = ASSETS_DIR / f"{diagram_name}.mmd"
            png_path = ASSETS_DIR / f"{diagram_name}.png"
            
            # 1. Write the raw Mermaid syntax to a temporary .mmd file
            mmd_path.write_text(match.strip(), encoding="utf-8")
            
            print(f"🎨 Generating {png_path.name}...")
            
            # 2. Call the Mermaid CLI to render the image
            try:
                # npx allows us to run the CLI without installing it globally
                cmd = ["npx", "-p", "@mermaid-js/mermaid-cli", "mmdc", "-i", str(mmd_path), "-o", str(png_path), "-b", "transparent", "-t", "dark"]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to render {png_path.name}. Do you have Node.js/npx installed?")

    print(f"\n✅ Done! Successfully generated {diagram_count} architecture images in {ASSETS_DIR}")

if __name__ == "__main__":
    generate_architecture_images()