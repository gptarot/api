export interface Prediction {
  data: string;
}

export interface PredictionRequest {
  name: string;
  dob: string;
  question: string;
  pastCard: string;
  presentCard: string;
  futureCard: string;
}

export interface InputProps {
  id: string;
  onChange: (ev: React.ChangeEvent<HTMLInputElement>) => void;
  value: string;
  label: string;
  type?: string;
  error?: string;
}

export interface Cards {
  pastCard: string;
  presentCard: string;
  futureCard: string;
}

export interface ReactChild {
  children: string | JSX.Element | JSX.Element[];
}

export interface CardInfo {
  name: string;
  number: string;
  arcana: string;
  suit: string;
  img: string;
  fortune_telling: string[];
  keywords: string[];
  meanings: {
    light: string[];
    shadow: string[];
  };
  Archetype: string;
  'Hebrew Alphabet': string;
  Numerology: string;
  Elemental: string;
  'Mythical/Spiritual': string;
  'Questions to Ask': string[];
}
