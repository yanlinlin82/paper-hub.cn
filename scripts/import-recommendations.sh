for f in /work/Research/PubMed-Mining/recommendations/*.xlsx; do
	time python scripts/do-import-recommendations.py $(basename $f | cut -d. -f1-2) $f
done
