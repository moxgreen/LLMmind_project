# written with AI assistance: Claude Code, Claude Opus 5.5 (claude-opus-5-5)
# last AI edit: 2026-11-26, see docs/changelog/developers/ for details
import argparse
import re

import pandas as pd

from libraries.parquet_io import read_parquet

NSD_SUBJECTS = [f"subject{i}" for i in range(1, 9)]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nsd_stimulus_info",
                        required = True)
    parser.add_argument("--nsd_brain_embeddings",
                        required = True)
    parser.add_argument("--caption_scene_brain_embeddings",
                        required = True)
    parser.add_argument("--caption_scene_stimulus_index",
                        required = True)
    parser.add_argument("--image_overlap",
                        required = True)
    args = parser.parse_args()

    # retained NSD images: concept nsd-NNNNN holds the 1-based 73k ID, nsdId = 73k ID - 1
    info = pd.read_csv(args.nsd_stimulus_info)
    nsd_ids = [
        int(concept.split("-")[1]) - 1
        for concept in read_parquet(args.nsd_brain_embeddings).index
    ]
    nsd = info.set_index("nsdId").loc[nsd_ids]
    nsd_coco = set(nsd["cocoId"])

    # retained Caption Scene images: the COCO ID ends the concept name
    caption_scene = read_parquet(args.caption_scene_brain_embeddings).index
    caption_scene_coco = {
        int(re.search(r"_(\d+)$", concept).group(1))
        for concept in caption_scene
    }

    # every image of each dataset
    index = pd.read_csv(
        args.caption_scene_stimulus_index,
        sep = "\t",
        header = None,
        encoding = "latin-1",
    )
    caption_scene_all = {
        int(match.group(1))
        for value in index[1].astype(str)
        for match in [re.search(r"COCO_\w+2014_(\d+)\.jpg", value)]
        if match
    }
    nsd_all = set(info["cocoId"])

    # count the overlaps and save them
    both = sorted(nsd_coco & caption_scene_coco)
    counts = {
        "nsd_retained": len(nsd_ids),
        "nsd_retained_seen_by_2_or_more_subjects": int(
            (nsd[NSD_SUBJECTS].sum(axis = 1) >= 2).sum()
        ),
        "nsd_retained_in_shared1000": int(nsd["shared1000"].sum()),
        "caption_scene_retained": len(caption_scene),
        "retained_in_both": len(both),
        "retained_in_both_coco_ids": ",".join(str(coco_id) for coco_id in both),
        "caption_scene_all": len(caption_scene_all),
        "nsd_all": len(nsd_all),
        "caption_scene_all_in_nsd_all": len(caption_scene_all & nsd_all),
        "caption_scene_retained_in_nsd_all": len(caption_scene_coco & nsd_all),
        "nsd_retained_in_caption_scene_all": len(nsd_coco & caption_scene_all),
    }
    pd.DataFrame({"statistic": list(counts), "value": list(counts.values())}).to_csv(
        args.image_overlap,
        sep = "\t",
        index = False,
    )

if __name__ == "__main__":
    main()
