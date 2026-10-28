# Microbiome simulation and quality-control demo

This is a small, standalone Python demonstration of microbiome count-data simulation and quality checks. It grew out of questions I explored during the **BIOT670I Microbiome Abundance Consensus Machine** group capstone: before comparing statistical methods, how can we tell whether our input data and metadata are consistent?

In the broader team project, Python supported simulation, preparation, and organization of analysis files. R provided the packages used for ALDEx2, ANCOM-BC2, and DESeq2; CLR/Wilcoxon was also evaluated. **This portfolio example does not implement those four differential-abundance tests or reproduce the team's published/unpublished results.** It focuses on the validation work that precedes statistical testing.

## What the example does

- Generates an illustrative, entirely synthetic case/control count table (40 samples, 60 taxa) with no deliberately introduced group effect.
- Varies library sizes and sample compositions while using the same data-generating mechanism in both groups.
- Saves a count table, sample metadata, and a separately stored null truth table.
- Checks sample alignment, count integrity, library-size consistency, and ground-truth labels.
- Summarizes sequencing-depth variation, zero fractions, and taxon prevalence; optionally makes a plot.

**Why null data?** With no intended group difference, null simulations are useful for validating an analysis pipeline before more complex benchmarking. They do *not* by themselves show that a differential-abundance method controls Type I error: repeated simulations and formal hypothesis testing would be needed for that claim.

## Run locally

Python 3.10+ is recommended.

```bash
python -m pip install -r requirements.txt
python -m scripts.simulate_null --output-dir outputs --seed 42
python -m scripts.validate_counts --input-dir outputs
python -m scripts.summarize_qc --input-dir outputs
python -m unittest discover -s tests -v
```

The commands write generated CSVs and a PNG to `outputs/`, which is git-ignored. The results are reproducible for the specified seed and dependency versions, but exact random outputs can vary across NumPy versions.

## Files

- `scripts/simulate_null.py`: synthetic data generation; no real patient or study data.
- `scripts/validate_counts.py`: input integrity checks; exits with an error for failed checks.
- `scripts/summarize_qc.py`: QC statistics and a library-size figure.
- `tests/test_workflow.py`: basic positive and negative tests.

## Scientific decisions and limitations

This example uses a shared baseline composition with sample-level Dirichlet variation, a Poisson-distributed library size, and multinomial sampling of counts. The parameters are chosen for demonstrating software checks, **not fitted to a real microbiome study**. The generated data therefore cannot establish the performance of any differential-abundance method or the biological realism of a simulator. The truth table is kept separate from count/metadata inputs because truth labels belong in downstream evaluation, not in statistical model fitting.

The main lesson I wanted to capture from this part of the capstone is simple: code that runs is not necessarily evidence that its inputs are correct. Data alignment and explicit QC are worth checking before interpreting results.

## Relationship to the group project

This is a **separate educational portfolio example**, newly organized with synthetic data. It is not a copy of the original group repository and contains no real-data arm, complete consensus analysis, or original team results. Credit for the wider capstone concept belongs to the BIOT670I project team. Please consult the original project and collaborators for any future research use of shared material.

## Acknowledgment

This portfolio package was prepared with AI assistance and is intended for personal review and verification before public release.
