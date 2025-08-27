import { z } from "zod";

/**Papers */
export const AuthorSchema = z.object({
  _id: z.string().optional(),
  full_name: z.string(),
  last_name: z.string(),
  first_name: z.string(),
});

export const PaperSchema = z.object({
  _id: z.string(),
  bibtex_id: z.string(),
  title: z.string(),
  authors: z.array(AuthorSchema),
  year: z.number(),
  publication_date: z.string(),
  journal: z.string(),
  publisher: z.string(),
  volume: z.string(),
  doi: z.string(),
  url: z.string(),
  isbn: z.string(),
  issn: z.string(),
  abstract: z.string(),
  keywords: z.array(z.string()),
  screening_status: z.string(),
  screening_notes: z.string(),
  labels: z.array(z.string()),
  imported_from: z.string(),
  source_file: z.string(),
  __v: z.number().optional(),
  updatedAt: z.string().optional(),
});

export type Author = z.infer<typeof AuthorSchema>;
export type Paper = z.infer<typeof PaperSchema>;
export const GetAllPapersResponseSchema = z.object({
  papers: z.array(PaperSchema),
  stats: z.object({
    all: z.number(),
    pending: z.number(),
    included: z.number(),
    excluded: z.number(),
    maybe: z.number(),
  }),
  filter: z.string(),
  total: z.number(),
});
export type GetAllPapersResponse = z.infer<typeof GetAllPapersResponseSchema>;

export const ToLabelResponseSchema = z.object({
  message: z.string(),
  labels: z.array(z.string()),
});

export type ToLabelResponse = z.infer<typeof ToLabelResponseSchema>;
export type FilterStatusPapers =
  | "all"
  | "pending"
  | "included"
  | "excluded"
  | "maybe";
