import mongoose, { Schema, Document } from "mongoose";

interface IAuthor {
  full_name: string;
  last_name: string;
  first_name: string;
}

export interface IPaper extends Document {
  bibtex_id: string;
  title: string;
  authors: IAuthor[];
  year: number;
  publication_date: string;
  journal: string;
  publisher: string;
  volume: string;
  doi: string;
  url: string;
  isbn: string;
  issn: string;
  abstract: string;
  keywords: string[];
  screening_status: string;
  screening_notes: string;
  imported_from: string;
  source_file: string;
}

const AuthorSchema = new Schema({
  full_name: String,
  last_name: String,
  first_name: String,
});

const PaperSchema = new Schema(
  {
    bibtex_id: {
      type: String,
      required: true,
      unique: true,
    },
    title: {
      type: String,
      required: true,
    },
    authors: [AuthorSchema],
    year: {
      type: Number,
      required: true,
    },
    publication_date: String,
    journal: String,
    publisher: String,
    volume: String,
    doi: String,
    url: String,
    isbn: String,
    issn: String,
    abstract: String,
    keywords: [String],
    screening_status: {
      type: String,
      default: "pending",
    },
    screening_notes: {
      type: String,
      default: "",
    },
    labels: [String],
    imported_from: String,
    source_file: String,
  },
  { timestamps: true }
);

const Paper = mongoose.model<IPaper>("Paper", PaperSchema);

export default Paper;
