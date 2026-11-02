
import React from 'react';
import { Sparkles, BookOpen, Globe, ShieldCheck } from 'lucide-react';

export const AboutPage: React.FC = () => {
  const features = [
    {
      icon: Globe,
      title: 'Multilingual Understanding',
      description: 'Ask questions in English, Hindi, Marathi, Bengali, Tamil, Telugu, Spanish, French, German and Arabic.',
    },
    {
      icon: BookOpen,
      title: 'Retrieval-Augmented Generation',
      description: 'ARI searches your uploaded documents and uses relevant passages to generate grounded answers.',
    },
    {
      icon: ShieldCheck,
      title: 'Source-Based Answers',
      description: 'Answers include document references so you can verify where information came from.',
    },
  ];

  return (
    <div className="min-h-screen bg-ari-bg px-6 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <Sparkles className="w-12 h-12 text-ari-mauve mx-auto mb-4" />
          <h1 className="text-4xl font-serif font-bold text-ari-text mb-3">
            About ARI
          </h1>
          <p className="text-ari-secondary text-lg">
            Knowledge, in every language.
          </p>
        </div>

        <div className="glass-panel rounded-3xl p-8 mb-8">
          <h2 className="text-2xl font-semibold text-ari-text mb-4">
            Meet ARI
          </h2>
          <p className="text-ari-secondary leading-8">
            ARI is a multilingual Retrieval-Augmented Generation assistant
            designed to help users explore their documents, ask questions
            across languages and receive answers supported by retrieved
            information.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map(({ icon: Icon, title, description }) => (
            <div key={title} className="glass-panel rounded-2xl p-6">
              <Icon className="w-8 h-8 text-ari-mauve mb-4" />
              <h3 className="font-semibold text-ari-text mb-3">{title}</h3>
              <p className="text-sm text-ari-secondary leading-7">
                {description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
