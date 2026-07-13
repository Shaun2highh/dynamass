# Submitting the note to AAS Research Notes — runbook

The package is final: `note_catalog_artifacts.tex` (626 body words; limit
1000) + `results/note_fig1_barnard.png`. One substitution and four steps
remain, all requiring your personal accounts (~1 hour total).

## Step 1 — publish the code (10 min)

The note cites the repository; do this first.

1. Create a GitHub account if needed → create a new **public** repo named
   `dynamass` (no README — we have one).
2. In a terminal:
   ```bash
   cd ~/proj
   git remote add origin https://github.com/<YOUR-USER>/dynamass.git
   git push -u origin main
   ```
3. In `note_catalog_artifacts.tex`, replace the single token
   `[GITHUB-URL]` with `https://github.com/<YOUR-USER>/dynamass`.

(Zenodo DOI: optional now, better later — after acceptance, log into
zenodo.org with GitHub, flip the switch on the repo, create a release;
Zenodo mints a DOI you can add at proof stage.)

## Step 2 — AAS account (5 min)

Register at https://journals.aas.org (free). RNAAS has **no publication
charge**.

## Step 3 — submit (30–40 min of form-filling)

1. Go to the AAS submission portal, choose **Research Notes of the AAS**.
2. Upload `note_catalog_artifacts.tex` and `note_fig1_barnard.png`
   (copy the PNG next to the .tex first, or upload from results/).
3. Title/author/affiliation fields: as in the .tex ("Independent
   Researcher" is acceptable).
4. Suggested keywords: Exoplanet dynamics; Exoplanet catalogs;
   N-body simulations; Radial velocity.
5. The AI-assistance disclosure is already in the manuscript text (last
   paragraph); if the form has a separate AI-use question, answer yes and
   point to that paragraph.
6. Submit. RNAAS is moderated (not peer-reviewed); decisions typically
   arrive in days–weeks. Notes are published as-is — proofread before
   clicking.

## Step 4 — after acceptance

- Mint the Zenodo DOI (step 1 note) and send it with proofs if offered.
- Add the citation to the main survey paper's companion-note reference.

## Sanity checklist before clicking submit

- [ ] `[GITHUB-URL]` replaced and the repo is public
- [ ] You have read every sentence and agree with it — moderation is
      light; the responsibility is yours
- [ ] Email in the .tex is the one you want public
- [ ] Figure displays correctly in the portal's compiled preview
