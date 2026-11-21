---
name: recipe-manager
description: USE THIS FIRST for any recipe work. Covers recipe creation (formatting ingredients, writing methods, setting measurements and timing) and recipe organization (categorizing, tagging, managing sources). Use when user asks to create, format, finalize, write, organize, or categorize recipes.
metadata:
  hermes:
    tags:
    - recipes
    - cooking
---

# Recipe Manager

A comprehensive system for writing, formatting, and organizing recipes.

---

## SECTION 1: Recipe Writing & Formatting

### Use Cases for This Section

This section serves two purposes:

1. **Reference guide** - Best practices for formatting ingredients and writing recipes
2. **Recipe documentation** - Standard format for writing/creating recipes, whether dictating, typing, or providing partial information

**The format below is designed to work with Crouton's import system.**

### Recipe Documentation Format

When writing or creating a recipe, follow this structure for Crouton's "From Text" import:

```
## [Recipe Name]

Serves: [number]
Prep Time: [time]
Cook Time: [time]

Ingredients:

[Section Name 1]
[ingredient 1] (parentheses can include notes)
[ingredient 2]

[Section Name 2]
[ingredient 3]
...

Steps:


[Section Name 1]

[instruction 1]

[instruction 2]

[instruction 3]


[Section Name 2]

[instruction 4]

[instruction 5]

[instruction 6]

Notes:

[observations, tips, variations]
```

**Crouton field constraints:**

**Serves:**
- Must be a **whole number only**
- If given a range (e.g., "serves 4-6"), use the minimum number
- Add full range to Notes section: `Serves 4-6 people`
- For detailed yield info (e.g., "2 tacos per person"), put the number in Serves, put the detail in Notes

**Prep Time / Cook Time:**
- Must be **fixed time values only** (e.g., "25 min", "1 hr")
- Represent active work time, not rest/marinating/passive time
- If additional time is mentioned (overnight rest, marinating, cooling), add to Notes section
- Examples:
  - Dictated: "20 minutes prep plus overnight rest"
  - Format: `Prep Time: 20 min` + Note: `Requires overnight rest before cooking`

**Mapping professional terminology to Crouton fields:**
- **Active Time** (hands-on work) → approximates to **Prep Time**
- **Total Time** (including passive time like rising, marinating, resting) → does not map directly; put Cook Time for actual cooking, and add passive time details to Notes
- When in doubt, defer extra timing information to Notes

**Critical formatting rules for Crouton import:**

**Ingredients section:**
- Start with `Ingredients:` header
- Can include section names to organize ingredients (e.g., "For the Sauce", "For the Filling")
- Section name on its own line, then ingredients below
- Blank line between sections
- Ingredients can have notes in parentheses (see "What Can Go in Ingredient Parentheses" below)
- Example:
  ```
  Ingredients:
  
  For the Chiles
  6 chiles guajillo
  6 chiles ancho (dried)
  4 chipotles en adobo
  
  For the Seeds
  ¼ cup walnuts (al gusto)
  ¼ cup pepitas (al gusto)
  ¼ cup almonds (al gusto)
  ```

**Instructions/Steps section:**
- Start with `Steps:` header
- **NO bullets, NO numbers** - just plain text
- **Blank line after each instruction** (two newlines total)
- **DOUBLE blank lines before each section name** (three newlines total)
- Example:
  ```
  Steps:
  
  
  For the Chiles
  
  Remove stems and seeds from chiles.
  
  Heat oil in pan and fry chiles lightly.
  
  Place in bowl with hot broth to soak.
  
  
  For the Spices
  
  Toast sesame seeds until golden.
  
  Toast cumin and cinnamon briefly.
  ```

**Import workflow:**
1. Paste formatted text into Crouton → Plus icon → "From Text"
2. After import, go to Bulk Edit for ingredients → paste ingredient section
3. Go to Bulk Edit for method/instructions → paste Steps section
4. Sections will then appear properly organized

---

### Capturing Recipe Context

Recipes often come with more than just ingredients and steps — intros, descriptions, backstories, author tips, substitutions, and recommendations. Whether dictating your own recipe, processing one from a website, or working from an image, extract this surrounding context and place it where it's useful.

**What to look for:**
- Ingredient-specific tips ("use fresh-squeezed orange juice, not bottled")
- Brand recommendations ("I prefer Diamond Crystal kosher salt here")
- Substitution options
- Technique notes or warnings ("don't skip the resting step")
- Serving suggestions or pairings
- Personal observations or lessons learned

**Three places to distribute contextual information:**

**1. Ingredient parentheses** — tips specific to a single ingredient:
- `1 cup orange juice (fresh-squeezed preferred)`
- `½ cup sour cream (or Mexican crema)`
- `1 tbsp fish sauce (Red Boat recommended)`
- `2 lbs chicken thighs (bone-in works best here)`

**2. Steps** — technique tips that belong in the flow of cooking:
- Weave process-specific advice directly into the relevant instruction
- Example: Instead of a generic "sauté onions," include the tip: "Sauté onions over medium heat until deeply golden, about 15 minutes — don't rush this step, the flavor depends on it"

**3. Notes section** — the catch-all for everything else (see "Notes Section Usage" below for full list)

---

### Recipe Writing Standards

The following standards are adapted from professional kitchens and publications (*Bon Appétit*, *Food52*, *NYT Cooking*) for personal use to ensure reliable, repeatable recipes.

#### Recipe Title & Description

**Title:**
- Be descriptive and specific
- Avoid vague names: use "Red Wine Braised Beef Stew" not "Grandma's Stew"

**Headnote (optional 2-3 sentences):**
- What the dish is and what to expect (texture, flavor)
- Any crucial context (e.g., "Dough needs to rest overnight, plan ahead")
- *Note: Crouton doesn't currently support a description field. Place headnote content in the Notes section until this is added.*

#### Yield & Timing Precision

**Yield:**
- Be specific: "Serves 4 (2 tacos per person)" or "Makes 12 muffins"
- *For Crouton: Put just the number in Serves field, put the detail in Notes*
  - Example: Serves field = `4`, Notes = `Serves 4 (2 tacos per person)`

**Time breakdown (professional standard):**
- **Active Time:** Hands-on work (chopping, stirring, assembling)
- **Total Time:** Including passive time (rising, marinating, baking, resting)
- *For Crouton: Map Active Time → Prep Time, cooking duration → Cook Time, and add any passive/resting time to Notes*

### Ingredient Formatting

#### What Can Go in Ingredient Parentheses

Parentheses in ingredient lines are flexible. Use them for:

- **Weight/count conversions:** `2 medium russet potatoes (about 500g total)`
- **Volume equivalents:** `250g all-purpose flour (about 2 cups)`
- **Prep state clarifications:** `1 lb chicken thighs (boneless, skinless)`
- **Substitutions for that ingredient:** `½ cup sour cream (or Mexican crema)`
- **Brand recommendations:** `1 tbsp fish sauce (Red Boat recommended)`
- **Freshness/quality notes:** `1 cup orange juice (fresh-squeezed preferred)`
- **Flexible quantities:** `¼ cup pepitas (al gusto)`
- **Brief tips:** `2 lbs brisket (fat cap on for better moisture)`

Keep parenthetical notes concise. If the note is longer or applies to multiple ingredients, put it in the Notes section instead.

#### Measurement Best Practices

Professional recipe developers recommend using **both weight and count measurements** strategically to balance precision with practical usability.

**The Hybrid Approach (Professional Standard):**

**For whole produce/vegetables:**
- Format: `2 medium russet potatoes (about 250g each)` or `500g russet potatoes (about 2 medium)`
- **Count first** for shopping guidance
- **Weight in parentheses** for cooking precision

**For baking ingredients:**
- Format: `250g all-purpose flour (about 2 cups)` or `2 cups (250g) all-purpose flour`
- **Weight first** for precision (density variations matter in baking)
- Volume as secondary reference for those without scales

**When to Prioritize Weight (Grams):**
- Baking ingredients where precision matters (flour, sugar, butter)
- Scaling recipes up or down
- Ingredients with density variations (shredded cheese, chopped nuts, packed brown sugar)
- Personal consistency — weight ensures you can recreate your own recipes reliably

**When Count/Volume Works Better:**
- Whole produce where shopping is easier with count ("2 carrots" vs estimating 300g at store)
- Recipes where precision matters less (a few extra grams of onion won't hurt most savory dishes)
- Common sense ingredients (experienced cooks understand "1 medium onion" flexes based on availability)

**Small quantities:**
- Keep amounts under 1 tablespoon in volume measurements
- Most home scales aren't sensitive enough below 5-10g

**Prep state clarity:**
- `250g cauliflower florets` (weight after trimming)
- `1 small cauliflower (250g), cut into florets` (weight before prep)
- Be explicit about whether weight is before or after prep

---

#### The "Comma Rule" for Ingredients

Critical for measurement accuracy:

- **"1 cup walnuts, chopped"** → Measure whole walnuts first, *then* chop
- **"1 cup chopped walnuts"** → Chop first, *then* measure the chopped result

**State of ingredient:**
- Specify before cooking: "unsalted butter, melted" or "eggs, room temperature"

#### Ingredient List Organization

- **Chronological order:** List in order of use in instructions
- **Sub-headers:** Use sections for distinct components (e.g., "For the Dressing", "For the Salad", "For the Marinade")
- **Divided ingredients:** Note in list (e.g., "1 cup sugar, divided") and specify amount in instructions

#### Method/Instructions Best Practices

**Structure:**
- Steps with imperative verbs
- Action verbs first: "Whisk", "Sauté", "Fold"

**Sensory cues (critical):**
- Never rely on time alone
- Always pair time with visual/sensory indicator
- ❌ Incorrect: "Cook for 5 minutes"
- ✅ Correct: "Cook until onions are translucent and soft, about 5 minutes"

**Specificity:**
- Include heat level and vessel size
- ✅ "Heat oil in a 12-inch skillet over medium-high heat"
- ❌ "Heat oil in a pan"

**Doneness indicators:**
- Visual cues: "golden brown", "bubbling vigorously", "set around edges"
- Texture cues: "tender when pierced with fork", "springs back when touched"
- **Temperature when critical: "165°F internal temperature"**

**Internal temperature best practice (Combustion Inc Predictive Thermometer integration):**

Always include target internal temperatures for proteins and baked goods when relevant. This is both a food safety best practice and enables Crouton's integration with the Combustion Inc predictive thermometer.

When to include internal temps:
- **All proteins:** Chicken, beef, pork, fish, etc.
- **Baked goods:** Bread, cakes when precision matters
- **Any dish where doneness is temperature-critical**

**Format in instructions:**
- ✅ "Roast until chicken reaches an internal temperature of 165°F, about 45-50 minutes"
- ✅ "Grill steak to an internal temperature of 135°F for medium-rare, 8-10 minutes"
- ✅ "Bake until internal temperature reaches 190°F and crust is golden, 35-40 minutes"

**Why this matters:**
1. **Food safety:** Ensures proteins reach safe temperatures
2. **Consistency:** Removes guesswork, makes recipes repeatable
3. **Crouton integration:** Target temps in steps can be set directly on the predictive thermometer from within Crouton
4. **Professional standard:** Temperature is the most reliable doneness indicator

**Combustion Inc Predictive Thermometer workflow:**
When target temps are mentioned in recipe steps, Crouton allows you to set the thermometer's target directly from that step, enabling hands-free monitoring and notifications when food reaches target temperature.

---

### Notes Section Usage

The Notes section is the catch-all for valuable information that doesn't fit in ingredients or steps. Use it for:

**From Crouton field constraints:**
- Serving range if applicable (e.g., "Serves 4-6 people")
- Detailed yield info (e.g., "2 tacos per person")
- Rest/marinating/passive time requirements
- Headnote/description content (until Crouton adds a description field)

**From recipe context (intros, backstories, author tips):**
- Substitutions affecting multiple ingredients: "Greek yogurt can replace sour cream throughout"
- Technique insights: "Letting the dough rest overnight develops better flavor"
- Equipment notes: "Cast iron works better than stainless here"
- Personal observations: "I found the original recipe too salty — reduced by half"
- Serving suggestions or pairings

**General recipe information:**
- **Storage:** How long it keeps, freezing instructions
- **Make-ahead:** What can be prepped in advance
- **Variations:** Optional additions or changes
- **Troubleshooting:** Common issues and solutions

---

## SECTION 2: Recipe Organization & Management

### Current Implementation: Crouton

**Crouton = Single source of truth for ALL recipes**

The recipe itself always lives in Crouton, regardless of source. External systems (Paperless, Obsidian) are only for preserving source materials and research, never the recipe itself.

#### Recipe Source Patterns

Every recipe follows ONE of these five patterns:

**Pattern 1: Web source**
- Recipe found online
- **Source field**: Web URL
- **Notes section**: (optional) cooking notes only
- Example: Recipe from NYT Cooking, Serious Eats, etc.

**Pattern 2: PDF/Image source (not from owned book)**
- Recipe from PDF or photo that you don't have physical access to
- **Source field**: Could be Paperless link (experiment with this)
- **Notes section**: Paperless link if not in source field
  - Format: `Archive: https://paperless.yourdomain.com/documents/[ID]`
- Example: Downloaded PDF, screenshot, recipe from someone else

**Pattern 3: Owned cookbook**
- Recipe from a physical book you own
- Process: Snap photo → Import to Crouton → Delete photo (book is the source)
- **Source field**: (empty or book name)
- **Notes section**: Book reference for easy lookup
  - Format: `Source: [Book Title], p. [page number]`
  - Example: `Source: Brunch at Bobby's, p. 23`
- No Paperless/Obsidian needed - the physical book is your archive
- Example: Almond croissant from Brunch at Bobby's book

**Pattern 4: Synthesized/Researched recipe**
- Recipe created from combining multiple sources with research
- Iterative development, multiple sources/videos referenced
- **Source field**: (empty or "Original - Synthesized")
- **Notes section**: Obsidian URI link using Advanced URI plugin
  - Format: `Research: obsidian://open?vault=[vault]&file=[UUID]`
  - UUID-based link remains stable even if note filename changes
  - Obsidian note contains: source links, research, iteration history, synthesis reasoning
- After iterations, final recipe lands in Crouton as single source of truth
- Example: Chili recipe combining techniques from 3 different recipes and 2 videos

**Pattern 5: Original/Simple creation**
- Recipe created or adapted without needing external research archive
- May have looked at other recipes but not interested in saving them
- **Source field**: (empty or "Original")
- **Notes section**: Just cooking notes, observations, modifications
- No external links needed
- Examples: Tortillas de harina (looked at multiple but comfortable without archiving), Caldo de pollo (did research but not worth saving)

#### Quick Reference: Where to Find Source Info

- **URL in source field** → Web recipe
- **Paperless link** → PDF/image archive (not from owned book)
- **Book reference in notes** → Recipe from physical cookbook you own
- **Obsidian URI in notes** → Synthesized recipe with research archive
- **Just cooking notes** → Original/simple creation

#### Archive System Roles

- **Crouton**: Final recipe, cooking interface, searchability, organization
- **Paperless-NGX**: Frozen source documents only (PDFs, images)
- **Obsidian**: Dynamic research notes for synthesized recipes (links, iterations, reasoning)
- **Internet/Books**: Original sources remain available externally

#### Folder Structure

Recipes belong to ONE primary folder (though Crouton supports multiple):

- **Entrées** - Main dishes/proteins
- **Side Dishes** - Accompaniments, sides
- **Soups & Salads** - Soups, salads, stews
- **Breakfast & Brunch** - Morning foods, brunch items
- **Desserts** - Sweet treats, baked goods (cakes, cookies, pies)
- **Basics** - Building blocks for other recipes (stocks, sauces, doughs, marinades, compound butters, sandwich breads, dinner rolls, pizza dough, baguettes)
- **Snacks & Small Meals** - Substantial snacks, flexible meal items (protein shakes, energy bites, burritos that work for breakfast/snack/meal)

#### Folder Decision Logic

**Basics = "I make this TO USE in another recipe"**
**Everything else = "I make this AS the meal/dish itself"**

Special cases:
- Sweet breads (banana bread, zucchini bread) → Breakfast & Brunch or Desserts
- Side dish breads (cornbread, biscuits served as sides) → Side Dishes
- Techniques/templates (e.g., "Basic template for chili") → Basics
- Flexible items (meal-prep burritos) → Can use multiple folders OR use Snacks & Small Meals

#### Tag System

Tags are OPTIONAL - only apply if they help filter/find the recipe later.

**Tag Categories (with color coding):**

**🔵 BLUE - Proteins** (Most Important):
- Beef, Pork, Chicken, Turkey, Seafood, Vegetarian
- Add others as encountered (Duck, Lamb, etc.)

**🔴 RED - Cuisines**:
- American, Italian, Mexican, Asian, Chinese, Korean, Japanese, Indian, Middle Eastern, Thai, Vietnamese, etc.
- Only add specific cuisines, not generic ones
- "American" is often too generic unless distinctly American (BBQ, Southern fried chicken, etc.)

**🟢 GREEN - Occasions**:
- Weeknight, Entertaining, Holidays, Thanksgiving, Meal Prep

**🟣 PURPLE - Cooking Methods**:
- Slow Cooker, Instant Pot, One Pan, Grilled, Smoked
- Equipment-specific methods only

**🟡 YELLOW - Recipe Attributes** (Least Important):
- High Protein, Easy, Sandwiches

#### Tag Application Rules

**Critical rules:**
1. **Vegetarian tag = Entrées only** (and substantial meal-salads). Do NOT tag regular side dishes as vegetarian.
2. **Tags are optional** - Skip tags when folder alone is sufficient (e.g., basic pancakes in Breakfast & Brunch need no tags)
3. **Generic cuisines add no value** - Don't tag pancakes as "American"
4. **Basic techniques need no tags** - Oven-roasted chicken needs no cuisine tag; it's a technique

**When to skip tags entirely:**
- Basic recipes where folder is sufficient (plain pancakes, basic roasted vegetables)
- Techniques without specific cuisine (oven-roasted chicken, basic rice)
- Items where tags don't help filtering (banana bread in Breakfast & Brunch)

**When tags are valuable:**
- Cuisine helps filter (chicken korma → Indian, shawarma → Middle Eastern)
- Cooking method is equipment-specific (needs Slow Cooker, Instant Pot, Smoked)
- Occasion matters (Weeknight dinners, Meal Prep, holiday items)
- Format is searchable (Sandwiches tag for all sandwich/burger recipes)

#### Output Format

When categorizing a recipe, provide:

```
**[Recipe Name]**

Folder: [Folder name]
Tags: [Tag1] ([color]), [Tag2] ([color]), [Tag3] ([color])

Reasoning: [Brief explanation of choices]
```

If no tags are needed:
```
**[Recipe Name]**

Folder: [Folder name]
Tags: None needed

Reasoning: [Brief explanation]
```

#### Examples

**Italian Braised Chicken:**
Folder: Entrées
Tags: Chicken (blue), Italian (red), Slow Cooker (purple)
Reasoning: Main dish with clear cuisine and cooking method.

**Pancakes:**
Folder: Breakfast & Brunch
Tags: None needed
Reasoning: Basic breakfast item; folder is sufficient.

**Chicken Shawarma:**
Folder: Entrées
Tags: Chicken (blue), Middle Eastern (red), Meal Prep (green)
Reasoning: Specific cuisine, good for meal prep.

**Korean Braised Potato Side Dish:**
Folder: Side Dishes
Tags: Korean (red)
Reasoning: Side dish with specific cuisine. No Vegetarian tag (rule: sides don't get vegetarian tag).

**Basic Template for Making Chili:**
Folder: Basics
Tags: None needed
Reasoning: Technique/template, foundational knowledge.

**Burger Buns:**
Folder: Basics
Tags: None needed
Reasoning: Component made to use in other recipes.

**Banana Bread:**
Folder: Breakfast & Brunch
Tags: None needed
Reasoning: Sweet bread served as breakfast/snack. Folder is sufficient.

**Brisket:**
Folder: Entrées
Tags: Beef (blue), American (red), Smoked (purple)
Reasoning: Equipment-specific (smoker), distinctly American BBQ.
