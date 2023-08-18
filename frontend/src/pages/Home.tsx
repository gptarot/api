import { useState } from 'react';
import { getPrediction } from '../api/tarotAPI';
import Input from '@/components/Input';
import { Cards, Prediction } from '../types';

const Home: React.FC = (): JSX.Element => {
  const [name, setName] = useState<string>('');
  const [dob, setDob] = useState<string>('');
  const [question, setQuestion] = useState<string>('');
  const [cards, setCards] = useState<Cards>({
    pastCard: '',
    presentCard: '',
    futureCard: '',
  });
  const [prediction, setPrediction] = useState<Prediction | null>(null);

  const handleSubmit = async (ev: React.FormEvent<HTMLFormElement>): Promise<void> => {
    ev.preventDefault();

    const response: Prediction | undefined = await getPrediction(
      name,
      dob,
      question,
      cards.pastCard,
      cards.presentCard,
      cards.futureCard,
    );

    if (response) {
      setPrediction(response);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center z-10">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <Input
          id="name"
          label="Your name"
          onChange={(ev: React.ChangeEvent<HTMLInputElement>) => setName(ev.target.value)}
          value={name}
        />
        <Input
          id="dob"
          label="Your Day of Birth"
          onChange={(ev: React.ChangeEvent<HTMLInputElement>) => setDob(ev.target.value)}
          value={dob}
        />
        <Input
          id="question"
          label="Your Question"
          onChange={(ev: React.ChangeEvent<HTMLInputElement>) => setQuestion(ev.target.value)}
          value={question}
        />
        <div className="flex gap-4">
          <Input
            id="pastCard"
            label="Past Card"
            onChange={(ev: React.ChangeEvent<HTMLInputElement>) => setCards({ ...cards, pastCard: ev.target.value })}
            value={cards.pastCard}
          />
          <Input
            id="presentCard"
            label="Present Card"
            onChange={(ev: React.ChangeEvent<HTMLInputElement>) => setCards({ ...cards, presentCard: ev.target.value })}
            value={cards.presentCard}
          />
          <Input
            id="futureCard"
            label="Future Card"
            onChange={(ev: React.ChangeEvent<HTMLInputElement>) => setCards({ ...cards, futureCard: ev.target.value })}
            value={cards.futureCard}
          />
        </div>
        <div className="flex items-center justify-center">
          <button className="bg-white px-4 py-2 rounded-md">Submit</button>
        </div>
      </form>
      {prediction && <div className="bg-white p-4 rounded-md mt-10">{prediction.data}</div>}
    </div>
  );
};

export default Home;
