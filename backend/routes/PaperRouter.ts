import { Router } from "express";

import { PaperController } from "../controllers/PaperController";

const router = Router();

router.get("/", PaperController.getAllPapers);
router.get("/by-labels", PaperController.getPapersByLabels);
router.get("/:id", PaperController.getPaperById);
router.put("/:id/label", PaperController.toLabelPaper);
router.put("/:id/screening", PaperController.updateScreeningStatus);

export default router;
