import { Link } from 'react-router-dom';

const Navbar: React.FC = (): JSX.Element => {
  return (
    <div className="fixed flex gap-4 left-0 right-0 top-0 h-10 z-10">
      <Link to="/" className="text-white font-inter p-4">
        Home
      </Link>
      <Link to="/random" className="text-white font-inter p-4">
        Random Card
      </Link>
    </div>
  );
};

export default Navbar;
