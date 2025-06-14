
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AdminDashboard from "@/components/admin/AdminDashboard";

const Dashboard = () => (
  <>
    <Navbar />
    <main>
      <AdminDashboard />
    </main>
    <Footer />
  </>
);

export default Dashboard;
