# 🏷️ LinkWarden AI Tagging Suite

## 📌 Overview

**🚨 Temporary Solution 🚨**

This toolkit was created in response to [LinkWarden GitHub Issue #971](https://github.com/linkwarden/linkwarden/issues/971) as a temporary solution to manually run AI tagging on existing links. It is intended to be a community-driven solution until an official feature is fully implemented by the LinkWarden team.

Automatically tag your LinkWarden bookmarks using AI-powered tag generation! This suite of Python scripts leverages Ollama's language models to intelligently categorize your saved links based on their content.

## ⚠️ Important Notes

- This is a community-enhanced temporary solution
- Not an official LinkWarden feature
- Modified to support auto-generation and tag management
- Use at your own discretion - always backup your data first

## ✨ Features

- 🤖 **AI Auto-Generation**: Freely generate tags using any Ollama model
- 🔄 **Tag Merging**: Preserves existing tags while adding new AI-generated ones
- 📤 **Tag Export**: Extract all tags from your LinkWarden instance
- 🧹 **Tag Filtering**: Clean up unwanted tags by filtering to an allowed list
- 🔍 **Smart Content Analysis**: Analyzes link content, description, and title
- 🏗️ **Flexible Configuration**: Environment-based setup

## 🛠️ Prerequisites

- Python 3.8+
- LinkWarden instance with API access
- Ollama server (local or remote)
- Your preferred Ollama model (e.g., `gpt-oss:20b`, `phi3:mini-4k`, etc.)

## 📦 Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your `.env` file:
   ```env
   # Generate an API key from LinkWarden: Settings > Tokens > Create New Token
   LINKWARDEN_API_KEY=your_api_key_here

   # LinkWarden Base URL
   LINKWARDEN_BASE_URL=http://linkwarden.piipari.xyz/api/v1

   # Ollama Configuration
   OLLAMA_BASE_URL=https://ollama.piipari.xyz

   # Set to 'true' to skip links that already have tags
   SKIP_LINKS_WITH_TAGS=false
   ```

3. Generate a LinkWarden API Token:
   - Log into your LinkWarden instance
   - Navigate to **Settings > Tokens**
   - Click **Create New Token**
   - Copy and paste into `.env` file

## 🚀 Usage

### Three-Script Workflow

This toolkit provides three complementary scripts:

#### 1️⃣ **lw_tag_manager.py** - AI Tag Generation

Generates tags for your links using AI and **merges** them with existing tags (no tags are lost).

```bash
python3 lw_tag_manager.py
```

**What it does:**
- Fetches all links from LinkWarden
- Analyzes content using Ollama AI
- Auto-generates 1-5 relevant tags per link
- **Merges** new tags with existing ones (preserves all existing tags)
- Configurable via `SKIP_LINKS_WITH_TAGS` environment variable

**Model Configuration:**
Currently configured to use `gpt-oss:20b`. To change the model, edit line 63 in `lw_tag_manager.py`:
```python
"model": "your-preferred-model",
```

---

#### 2️⃣ **export_tags.py** - Tag Extraction

Extracts all unique tags from your LinkWarden instance and saves them to `tags.txt`.

```bash
python3 export_tags.py
```

**What it does:**
- Fetches all links and their tags
- Extracts unique tags
- Saves to `tags.txt` (sorted alphabetically)
- Includes helpful header comments

**Use this after:**
- Running AI tag generation
- Any time you want to review all tags in your system

---

#### 3️⃣ **filter_tags.py** - Tag Cleanup

Removes unwanted tags by filtering all links to only use tags listed in `tags.txt`.

```bash
python3 filter_tags.py
```

**What it does:**
- Reads allowed tags from `tags.txt`
- Shows what tags will be removed
- Asks for confirmation before proceeding
- Removes any tags NOT in the allowed list

**⚠️ Warning:** This is destructive - it removes tags! Review `tags.txt` carefully first.

---

### 📋 Recommended Workflow

```bash
# Step 1: Generate AI tags (merges with existing tags)
python3 lw_tag_manager.py

# Step 2: Export all tags to review what was created
python3 export_tags.py

# Step 3: Edit tags.txt - remove any nonsensical or unwanted tags
nano tags.txt  # or your preferred editor

# Step 4: Clean up - remove unwanted tags from all links
python3 filter_tags.py
```

This workflow lets you:
1. Let AI freely generate tags
2. Review what it created
3. Curate the tag list
4. Clean up any mess

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LINKWARDEN_API_KEY` | ✅ Yes | - | Your LinkWarden API token |
| `LINKWARDEN_BASE_URL` | ❌ No | `http://localhost:3002/api/v1` | LinkWarden API endpoint |
| `OLLAMA_BASE_URL` | ❌ No | `http://localhost:11434` | Ollama server endpoint |
| `SKIP_LINKS_WITH_TAGS` | ❌ No | `false` | Skip links that already have any tags |

### Tag File (`tags.txt`)

The `tags.txt` file is used by `filter_tags.py` to determine which tags to keep. Format:
```
# Comments start with #
programming
python
javascript
web-development
```

- One tag per line
- Lines starting with `#` are ignored
- Case-sensitive
- Blank lines are ignored

## 📋 Requirements

All dependencies are listed in `requirements.txt`:
- `requests` - API communication
- `python-dotenv` - Environment variable management
- `typing` - Type hints (built-in for Python 3.8+)
- `logging` - Logging (built-in)

## 🐛 Troubleshooting

### Authentication Errors
- Verify your `LINKWARDEN_API_KEY` is correct
- Check that your token hasn't expired
- Ensure your API key has proper permissions

### Ollama Connection Issues
- Verify `OLLAMA_BASE_URL` is correct and accessible
- Check that your Ollama server is running
- Test with: `curl https://your-ollama-url/api/tags`

### Model Not Found
- Ensure the model is pulled: `ollama pull gpt-oss:20b`
- Verify model name matches exactly (case-sensitive)

### No Tags Generated
- Check logs for errors
- Verify links have content (textContent, description, or name)
- Try lowering the minimum text length threshold

## 🔄 Differences from Original

This fork includes several enhancements:

- ✅ **Auto-generation**: Tags are generated freely, not restricted to a predefined list
- ✅ **Tag merging**: Existing tags are preserved when adding new ones
- ✅ **Export utility**: New `export_tags.py` script
- ✅ **Filter utility**: New `filter_tags.py` script for tag cleanup
- ✅ **Configurable model**: Easy to switch between Ollama models
- ✅ **Better logging**: More detailed debug information

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙌 Acknowledgments

- Original script: [dalekirkwood/LinkWarden_Manual_AI_Tag](https://github.com/dalekirkwood/LinkWarden_Manual_AI_Tag)
- [LinkWarden](https://github.com/linkwarden/linkwarden)
- [Ollama](https://ollama.ai)
- Inspiration: [LinkWarden Issue #971](https://github.com/linkwarden/linkwarden/issues/971)

---

🌟 **Happy Tagging!** 🏷️🚀

**Disclaimer:** This is a community-created tool and is not an official part of the LinkWarden project. Use with caution and always backup your data before running bulk operations.
