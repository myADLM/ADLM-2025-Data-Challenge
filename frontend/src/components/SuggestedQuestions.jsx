import { motion } from 'framer-motion';
import { Lightbulb } from 'lucide-react';

const SUGGESTED_QUESTIONS = [
  "What are the procedure steps for the 11-Deoxycortisol Serum assay?",
  "What equipment is used for the 25-Hydroxyvitamin D2 and D3 Serum assay?",
  "What reagents are required for the Acute Viral Hepatitis Profile?",
  "What is the LC-MS/MS system used for?",
  "What procedure steps involve centrifugation?",
  "What analytes are measured in serum specimens?",
  "What equipment is needed for spectrophotometry assays?",
  "What are the quality control steps for immunoassay analyzers?",
  "What specimen types are used for vitamin D testing?"
];

export default function SuggestedQuestions({ onSelect }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8"
    >
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="h-5 w-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Suggested Questions</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {SUGGESTED_QUESTIONS.map((question, index) => (
          <motion.button
            key={index}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            onClick={() => onSelect(question)}
            className="text-left p-4 bg-blue-50 hover:bg-blue-100 rounded-xl border border-blue-200 hover:border-blue-300 transition-all duration-200 group"
          >
            <p className="text-sm text-gray-800 group-hover:text-blue-700 font-medium">
              {question}
            </p>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}

