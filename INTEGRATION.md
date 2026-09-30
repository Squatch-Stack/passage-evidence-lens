# Portal integration contract

This interface is deliberately small enough to embed as a passage detail panel in an existing portal. Leipzig University Library's [renewal announcement](https://codexsinaiticus.org/en/project/renewal2022.aspx) describes React, Solr, IIIF, and Web Annotation data. The component does not assume access to their code or deployment.

## Proposed host input

```json
{
  "ref": "Luke.11.10",
  "source_uri": "https://codexsinaiticus.org/en/manuscript.aspx?book=35&chapter=11&verse=10",
  "witness_id": "GA-01",
  "artifact": {"uri": "host-supplied", "version": "host-supplied", "sha256": "host-supplied"},
  "rights": {"text": "source_link_only", "image": "source_link_only"},
  "reading_annotations": [],
  "canvas_uri": null,
  "review_status": "unreviewed"
}
```

The host decides whether text and image fields are available. The browser never infers permission from a public URL. A future IIIF Presentation 3 canvas URI can navigate to an institution-hosted image; Web Annotation selectors can identify a transcription span. The adapter must preserve the original native locus, correction hand, omission/uncertainty status, source version and locator. It must not turn textual similarity into an ancient copying edge.

## Clean handoff

1. Run the public link-only demo and the local rights-gated evaluation with the project's target users.
2. Obtain the Leipzig team's preferred component boundary, data contract, accessibility criteria, tests and contribution license.
3. Map the host's own IIIF/Web Annotation IDs into the contract, with source-specific rights decisions.
4. Keep this repo as a small reproducible reference implementation, or contribute the component to the upstream repository when its open-source release and contribution process are available.

No scraped images, current-site code, or project branding is required for the proof of concept.
