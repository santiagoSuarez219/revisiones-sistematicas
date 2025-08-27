import client from "../config/openai";
import { toLabelPaperPrompt } from "../prompts/toLabelPaperPrompt";

class PaperService {
  async getLabelsFromSummary(paperAbstract: string) {
    try {
      const response = await client.chat.completions.create({
        model: "gpt-5-nano",
        messages: [
          {
            role: "user",
            content: `${toLabelPaperPrompt} ${paperAbstract}`,
          },
        ],
      });

      const content = response.choices[0]?.message?.content;

      if (!content) {
        return [];
      }

      // ✅ Parsear el string JSON a array
      try {
        const labels = JSON.parse(content);
        return Array.isArray(labels) ? labels : [];
      } catch (parseError) {
        console.error("Error parsing OpenAI response:", parseError);
        console.error("Response content:", content);
        return [];
      }
    } catch (error) {
      console.error("Error calling OpenAI API:", error);
      throw new Error("Failed to get labels from OpenAI");
    }
  }
}

export default new PaperService();
