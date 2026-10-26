#!/usr/bin/env python3
"""
generate_record.py - builds the Week-13 Mini-Project lab record (Word .docx)
for PetCare - Full-Stack Pet Shelter and Adoption Management Platform.

Usage:
    pip install python-docx
    python generate_record.py                       # uses the defaults below
    python generate_record.py --name "A. Student" --roll 24501a44 --date 25-10-2026

Screenshots:
    Put your real screenshots in a folder called  screenshots/  next to this
    script, named exactly:
        screenshot1.png   Overview dashboard & metrics cards
        screenshot2.png   Pet registration form & management table
        screenshot3.png   http://localhost:5000/pets JSON response
    (.jpg / .jpeg also work). Any screenshot that is missing is replaced by a
    bordered placeholder box, so the document always builds.
"""
import argparse
import os
import sys
from datetime import date

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

# --------------------------------------------------------------------------
# 1. Student details (edit these, or pass --name / --roll / --date)
# --------------------------------------------------------------------------
STUDENT_NAME = "Your Name"
ROLL_NO = "24501a44"
WEEK_LABEL = "Week – 13"
SUBTITLE = "Mini - Project"
OUTPUT_FILE = "PetCare_Lab_Record_Week13.docx"
SCREENSHOT_DIR = "screenshots"

FONT = "Times New Roman"
CODE_FONT = "Courier New"

AIM = (
    "To design and develop PetCare – A Full-Stack Pet Shelter and Adoption "
    "Management Platform to register shelter pets, monitor adoption statuses, "
    "and manage records through a responsive dashboard."
)

INTRODUCTION = [
    "Animal shelters handle a constant flow of arrivals, health and age details, "
    "and adoptions. When this information is kept on paper or in scattered "
    "spreadsheets, it is hard to see which animals are still waiting for a home "
    "and which have already been adopted.",
    "PetCare is a web-based platform that keeps every shelter pet in one "
    "database. Staff register a pet, update its details, and mark it as adopted "
    "the moment the adoption happens. A live dashboard summarises the shelter "
    "at a glance: total pets, adopted pets, pets still available, and the most "
    "popular species. The whole workflow runs in the browser, so no extra "
    "software is needed on the staff computers.",
]

OBJECTIVES = [
    "Centralized pet record management in a single MongoDB database.",
    "Status tracking of every pet as Available or Adopted, with the adoption date.",
    "Complete CRUD operations (Create, Read, Update, Delete) through a RESTful API.",
    "A responsive user interface that works on desktop, tablet and mobile screens.",
]

TECHNOLOGIES = [
    ("Frontend", "HTML5, Modern CSS3, JavaScript ES6"),
    ("Backend", "Node.js, Express.js"),
    ("Database", "MongoDB Atlas / Mongoose"),
    ("Architecture", "RESTful API"),
    ("Development Tool", "Visual Studio Code"),
]

PROJECT_TREE = r"""PetCare_FullStack_Project/
|-- config/
|   `-- db.js                  - MongoDB connection (Mongoose)
|-- controllers/
|   `-- PetController.js       - CRUD logic for pets
|-- middleware/
|   |-- errorHandler.js        - Central error responses
|   `-- validId.js             - Validates :id parameters
|-- models/
|   `-- Pet.js                 - Pet schema and model
|-- routes/
|   `-- pets.js                - REST routes mounted at /pets
|-- public/                    - Frontend (served by Express)
|   |-- index.html             - Page structure
|   |-- style.css              - Responsive styling
|   `-- app.js                 - Fetch API calls and UI logic
|-- screenshots/               - Output screenshots for the record
|-- generate_record.py         - Builds this Word document
|-- index.js                   - Express server entry point
|-- .env.example               - Environment variable template
`-- package.json               - Dependencies and scripts"""

API_ROWS = [
    ("GET", "/pets", "List pets (filter: species, adopted; sort: age, name)"),
    ("POST", "/pets", "Register a new pet"),
    ("GET", "/pets/:id", "Fetch a single pet"),
    ("PUT", "/pets/:id", "Update details or adoption status"),
    ("DELETE", "/pets/:id", "Remove a pet record"),
]

CODE_BLOCKS = [
    ("models/Pet.js  –  Mongoose schema", r'''const mongoose = require("mongoose");

const petSchema = new mongoose.Schema({
    name: {
        type: String,
        required: [true, "Name is required"],
        trim: true
    },
    species: {
        type: String,
        enum: ['dog', 'cat', 'bird', 'rabbit', 'other'],
        default: 'other'
    },
    age: {
        type: Number,
        required: [true, "Age is required"],
        min: 0,
        max: 30
    },
    adopted: {
        type: Boolean,
        default: false
    },
    adoptedOn: {
        type: Date,
        default: null
    },
    arrivedOn: {
        type: Date,
        default: Date.now
    }
}, {
    timestamps : true
});

module.exports = mongoose.model("Pet", petSchema)'''),
    ("controllers/PetController.js  –  Pet controller methods", r'''const Pet=require('../models/Pet');

exports.getPets=async(req, res, next) => {
    try{
        const filter={};
        if (req.query.species) filter.species=req.query.species;
        if (req.query.adopted==="true") filter.adopted=true;
        if (req.query.adopted==="false") filter.adopted=false;

        let query=Pet.find(filter);

        if (req.query.sort==="age") query=query.sort({age:1});
        else if (req.query.sort==="name") query=query.sort({name:1});
        else query=query.sort({createdAt:-1});

        const pets=await query;
        res.status(200).json(pets);
    }catch(err){
        next(err);
    }
};

exports.getAvailablePets=async(req, res, next) => {
    try{
        const pets=await Pet.find({adopted:false});
        res.status(200).json(pets);
    }catch(err){
        next(err);
    }
};

exports.getPet=async(req, res, next) => {
    try {
        const pet=await Pet.findById(req.params.id);
        if (!pet) {
            return res.status(404).json({ 
                message:"Pet not found" 
            });
        }
        res.status(200).json(pet);
    } catch (err) {
        next(err);
    }
};

exports.createPet=async(req, res, next) => {
    try {
        const pet = new Pet(req.body);
        const savedPet = await pet.save();
        res.status(201).json(savedPet);
    } catch (err) {
        next(err);
    }
};

exports.updatePet=async(req, res, next) => {
    try {
        const existing = await Pet.findById(req.params.id);
        if (!existing) {
            return res.status(404).json({ 
                message:"Pet not found" 
            });
        }
        const update = { ...req.body };
        if (typeof update.adopted === "boolean" && update.adopted !== existing.adopted) {
            update.adoptedOn = update.adopted ? new Date() : null;
        }
        const pet = await Pet.findByIdAndUpdate(req.params.id, update, {
            new: true,runValidators: true
        });
        res.status(200).json(pet);
    } catch (err) {
        next(err);
    }
};

exports.deletePet=async (req, res, next) => {
    try {
        const pet=await Pet.findByIdAndDelete(req.params.id);
        if (!pet) {
            return res.status(404).json({
                message:"Pet not found"
            });
        }
        res.status(200).json({
            message:"Pet has deleted successfully!!"    
        });
    } catch (err) {
        next(err);
    }
};'''),
    ("routes/pets.js  –  Routes", r'''const express = require('express');
const c = require('../controllers/PetController');
const router = express.Router();
const validId = require('../middleware/validId');

router.get('/', c.getPets);
router.get('/available', c.getAvailablePets);

router.post('/', c.createPet);

router.get('/:id', validId, c.getPet);

router.put('/:id', validId, c.updatePet);

router.delete('/:id', validId, c.deletePet);

module.exports = router;'''),
    ("public/app.js  –  Frontend API fetch handlers", r'''/* ---------- API layer ---------- */
async function api(path = "", options = {}) {
  let res;
  try {
    res = await fetch(API + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error("Cannot reach the server. Check that it is running and try again.");
  }
  let data = null;
  try { data = await res.json(); } catch { /* non-JSON body */ }
  if (!res.ok) {
    const msg = (data && data.message) || `Request failed (${res.status})`;
    throw new Error(msg.replace(/^Pet validation failed:\s*/, ""));
  }
  return data;
}

const fetchPets = () => api("");
const createPet = (pet) => api("", { method: "POST", body: pet });
const updatePet = (id, changes) => api(`/${id}`, { method: "PUT", body: changes });
const deletePet = (id) => api(`/${id}`, { method: "DELETE" });'''),
    ("public/app.js  –  Actions that call the API", r'''async function toggleAdoption(pet) {
  try {
    const updated = await updatePet(pet._id, { adopted: !pet.adopted });
    replacePet(updated);
    toast(updated.adopted
      ? `${updated.name} is now marked as adopted.`
      : `${updated.name} is available for adoption again.`);
  } catch (err) { toast(err.message, "error"); }
}

async function removePet(pet) {
  try {
    const res = await deletePet(pet._id);
    state.pets = state.pets.filter((p) => p._id !== pet._id);
    if (state.editingId === pet._id) resetForm();
    render();
    toast(res.message || `${pet.name} was removed.`);
  } catch (err) { toast(err.message, "error"); }
}'''),
]

SCREENSHOTS = [
    ("Screenshot 1: Overview Dashboard & Metrics Cards", "screenshot1",
     "Capture the hero section with the four metric cards (Total Pets, Adopted, "
     "Available for Adoption, Most Popular Species)."),
    ("Screenshot 2: Pet Registration & Management Table", "screenshot2",
     "Capture the registration form beside the pet registry table showing the "
     "Edit, Mark adopted and Delete buttons."),
    ("Screenshot 3: Backend REST API Response in Browser (http://localhost:5000/pets)", "screenshot3",
     "Capture the browser tab at http://localhost:5000/pets showing the JSON "
     "array returned by the API."),
]

# --------------------------------------------------------------------------
# 2. Low-level helpers
# --------------------------------------------------------------------------
def set_run_font(run, name=FONT, size=12, bold=None, italic=None, color=None):
    run.font.name = name
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor(*color)


def para(doc_or_cell, text="", size=12, bold=False, italic=False, align=None,
         before=0, after=6, line=1.15, keep_next=False, left_indent=None):
    p = doc_or_cell.add_paragraph()
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.line_spacing = Pt(before), Pt(after), line
    pf.keep_with_next = keep_next
    if left_indent is not None:
        pf.left_indent = Inches(left_indent)
    if align is not None:
        p.alignment = align
    if text:
        set_run_font(p.add_run(text), size=size, bold=bold, italic=italic)
    return p


def heading(doc, text, size=12):
    return para(doc, text, size=size, bold=True, before=10, after=4, keep_next=True)


def bullet(doc, text, label=None):
    p = para(doc, after=2, left_indent=0.5)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    set_run_font(p.add_run("•\t"))
    p.paragraph_format.tab_stops.add_tab_stop(Inches(0.5))
    if label:
        set_run_font(p.add_run(label + ": "), bold=True)
    set_run_font(p.add_run(text))
    return p


def set_cell_borders(cell, size=6, color="808080", style="single", sides=("top", "left", "bottom", "right")):
    tcpr = cell._tc.get_or_add_tcPr()
    borders = tcpr.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tcpr.append(borders)
    for side in sides:
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), style)
        el.set(qn("w:sz"), str(size))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)


def shade_cell(cell, fill):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcpr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcpr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for k, v in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{k}")
        el.set(qn("w:w"), str(v))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcpr.append(mar)


def set_row_height(row, inches, exact=False):
    trpr = row._tr.get_or_add_trPr()
    h = OxmlElement("w:trHeight")
    h.set(qn("w:val"), str(int(inches * 1440)))
    h.set(qn("w:hRule"), "exact" if exact else "atLeast")
    trpr.append(h)


def cant_split(row):
    trpr = row._tr.get_or_add_trPr()
    trpr.append(OxmlElement("w:cantSplit"))


def add_page_border(section):
    """Single-line page border, same as the departmental template."""
    sectpr = section._sectPr
    borders = OxmlElement("w:pgBorders")
    borders.set(qn("w:offsetFrom"), "page")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "24")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    sectpr.append(borders)


def box(doc, fill="F5F5F5", border="808080"):
    """One-cell table used as a framed block; returns the cell."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    cell = t.rows[0].cells[0]
    cell.width = Inches(6.27)
    set_cell_borders(cell, color=border)
    if fill:
        shade_cell(cell, fill)
    set_cell_margins(cell)
    # remove the default empty paragraph
    cell._tc.remove(cell.paragraphs[0]._p)
    return t, cell


def code_block(doc, title, code, size=8):
    para(doc, title, size=11, bold=True, before=8, after=3, keep_next=True)
    _, cell = box(doc, fill="F3F3F3")
    lines = code.strip("\n").split("\n")
    # one paragraph per line keeps spacing exact and lets long blocks split across pages
    for i, ln in enumerate(lines):
        p = cell.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = pf.space_after = Pt(0)
        pf.line_spacing = 1.0
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(ln if ln else " ")
        set_run_font(run, name=CODE_FONT, size=size)
    para(doc, "", after=4)


def simple_table(doc, header, rows, widths, size=10.5):
    t = doc.add_table(rows=1, cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.width = Inches(widths[i])
        shade_cell(c, "E7E6E6")
        set_cell_borders(c)
        set_cell_margins(c, 50, 50, 100, 100)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(h), size=size, bold=True)
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].width = Inches(widths[i])
            set_cell_borders(cells[i])
            set_cell_margins(cells[i], 50, 50, 100, 100)
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            set_run_font(p.add_run(v), name=CODE_FONT if i < 2 else FONT, size=size - 1 if i < 2 else size)
    for i, w in enumerate(widths):  # also set grid widths so every viewer honours them
        t.columns[i].width = Inches(w)
    para(doc, "", after=2)


def find_image(base):
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(SCREENSHOT_DIR, base + ext)
        if os.path.isfile(path):
            return path
    return None


def screenshot_section(doc, caption, base, hint):
    para(doc, caption, size=12, bold=True, before=10, after=4, keep_next=True)
    path = find_image(base)
    if path:
        p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
        p.add_run().add_picture(path, width=Inches(6.0))
        print(f"  inserted {path}")
        return
    print(f"  placeholder for {base} (no image found in {SCREENSHOT_DIR}/)")
    t, cell = box(doc, fill="FAFAFA", border="7F7F7F")
    for side in ("top", "left", "bottom", "right"):  # dashed frame
        for el in cell._tc.tcPr.find(qn("w:tcBorders")):
            el.set(qn("w:val"), "dashed")
            el.set(qn("w:sz"), "12")
    set_row_height(t.rows[0], 3.0)
    cant_split(t.rows[0])
    tcpr = cell._tc.get_or_add_tcPr()
    va = OxmlElement("w:vAlign")
    va.set(qn("w:val"), "center")
    tcpr.append(va)
    for text, bold, size, col in (
        ("[ Insert " + caption.split(":")[0] + " here ]", True, 13, (0x40, 0x40, 0x40)),
        (hint, False, 10.5, (0x59, 0x59, 0x59)),
        ("Save it as " + SCREENSHOT_DIR + "/" + base + ".png and run this script again, "
         "or paste it directly into this box in Word.", False, 10, (0x7F, 0x7F, 0x7F)),
    ):
        p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        set_run_font(p.add_run(text), size=size, bold=bold, color=col)
    para(doc, "", after=4)


# --------------------------------------------------------------------------
# 3. Build the document
# --------------------------------------------------------------------------
def build(name, roll, date_text, output):
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)  # A4
    sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Inches(1)
    add_page_border(sec)

    # Header block: "Name: ....      RollNo: ...."  /  "Date: ...."
    p = para(doc, after=2)
    p.paragraph_format.tab_stops.add_tab_stop(Inches(6.27), WD_TAB_ALIGNMENT.RIGHT)
    set_run_font(p.add_run("Name"), bold=True, size=11)
    set_run_font(p.add_run(": " + name), size=11)
    set_run_font(p.add_run("\tRollNo: " + roll), bold=True, size=11)
    p = para(doc, after=8)
    set_run_font(p.add_run("Date"), bold=True, size=11)
    set_run_font(p.add_run(": " + date_text), size=11)

    para(doc, WEEK_LABEL, size=14, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(doc, SUBTITLE, size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=8)

    # Aim
    para(doc, "Aim:", size=14, bold=True, before=4, after=4, keep_next=True)
    para(doc, AIM, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # 1. Introduction
    heading(doc, "1. Introduction")
    for t in INTRODUCTION:
        para(doc, t, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # 2. Objective
    heading(doc, "2. Objective")
    for o in OBJECTIVES:
        bullet(doc, o)

    # 3. Technologies Used
    heading(doc, "3. Technologies Used")
    for label, text in TECHNOLOGIES:
        bullet(doc, text, label=label)

    # 4. Project Structure
    heading(doc, "4. Project Structure")
    _, cell = box(doc, fill="F3F3F3")
    for ln in PROJECT_TREE.split("\n"):
        p = cell.add_paragraph()
        p.paragraph_format.keep_with_next = True  # keep the whole tree on one page
        p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        set_run_font(p.add_run(ln), name=CODE_FONT, size=9)
    para(doc, "", after=4)
    para(doc, "REST API endpoints (mounted at /pets):", size=11, bold=True, after=3, keep_next=True)
    simple_table(doc, ("Method", "Endpoint", "Purpose"), API_ROWS, (0.9, 1.3, 4.07))

    # 5. Key Source Code
    heading(doc, "5. Key Source Code")
    for title, code in CODE_BLOCKS:
        code_block(doc, title, code)

    # 6. Output & Verification
    heading(doc, "6. Output & Verification")
    para(doc, "The server was started with npm start and the application was opened at "
              "http://localhost:5000. The following screens verify the working of the "
              "dashboard, the CRUD operations and the REST API.",
         align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    for caption, base, hint in SCREENSHOTS:
        screenshot_section(doc, caption, base, hint)

    doc.save(output)
    print("Saved", output)


def main():
    ap = argparse.ArgumentParser(description="Generate the Week-13 PetCare lab record (.docx)")
    ap.add_argument("--name", default=STUDENT_NAME)
    ap.add_argument("--roll", default=ROLL_NO)
    ap.add_argument("--date", default=date.today().strftime("%d-%m-%Y"))
    ap.add_argument("--out", default=OUTPUT_FILE)
    a = ap.parse_args()
    build(a.name, a.roll, a.date, a.out)


if __name__ == "__main__":
    sys.exit(main())
