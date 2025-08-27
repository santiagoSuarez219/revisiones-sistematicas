import type { Paper } from "../../types";

interface CardPaperProps {
    paper: Paper;
    onSelect: (paper: Paper) => void;
    isSelected?: boolean;
}

export default function CardPaper({ paper, onSelect, isSelected = false }: CardPaperProps) {
    const handleClick = () => {
        onSelect(paper);
    };

    return (
        <div
            className={`block w-full p-6 border rounded-lg shadow-sm cursor-pointer transition-all duration-200 ${isSelected
                    ? 'bg-blue-50 border-blue-300 dark:bg-blue-900/20 dark:border-blue-500'
                    : 'bg-white border-gray-200 hover:bg-gray-100 dark:bg-gray-800 dark:border-gray-700 dark:hover:bg-gray-700'
                }`}
            onClick={handleClick}
        >
            <h5 className={`mb-2 text-lg font-medium tracking-tight ${isSelected
                    ? 'text-blue-900 dark:text-blue-200'
                    : 'text-gray-900 dark:text-white'
                }`}>
                {paper.title}
            </h5>
            <p className={`font-normal text-base ${isSelected
                    ? 'text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-400'
                }`}>
                {paper.publication_date}
            </p>
            <p className={`font-normal text-base ${isSelected
                    ? 'text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-400'
                }`}>
                {paper.authors.map((author, index) => (
                    <span key={author._id}>
                        {author.full_name}
                        {index < paper.authors.length - 1 && ", "}
                    </span>
                ))}
            </p>
            <div className="font-normal text-gray-700 dark:text-gray-400 text-base mt-4 flex gap-1">
                {paper.labels.map((label, index) => (
                    <p className={`whitespace-nowrap text-xs font-semibold me-2 p-2 rounded-md border ${isSelected
                            ? 'bg-blue-200 text-blue-900 border-blue-500 dark:bg-blue-800 dark:text-blue-200'
                            : 'bg-blue-100 text-blue-800 border-blue-400 dark:bg-gray-700 dark:text-blue-400'
                        }`} key={index}>
                        {label}
                    </p>
                ))}
            </div>
        </div>
    );
}
