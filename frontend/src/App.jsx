import {
  LayoutDashboard,
  ScanLine,
  FileText,
  History,
  Settings,
  Bell,
  Search,
  Upload,
  ShieldCheck,
  AlertTriangle,
  Package,
  CheckCircle2,
  XCircle,
  Clock3,
  ChevronRight,
  Sparkles,
  Menu,
  ArrowLeft,
  Camera,
  FileCheck2,
  Info,
  Download,
  RotateCcw,
  Eye,
  Lock,
} 
from "lucide-react";
import { useState, useRef } from "react";


function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [active, setActive] = useState("Dashboard");
  const [selectedImage, setSelectedImage] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(false);

  const menu = [
    { name: "Dashboard", icon: LayoutDashboard },
    { name: "Scan Product", icon: ScanLine },
    { name: "Inspection History", icon: History },
    { name: "Reports", icon: FileText },
    { name: "Settings", icon: Settings },
  ];

  const inspections = [
    {
      product: "Premium Biscuits",
      manufacturer: "ABC Foods Pvt Ltd",
      score: 96,
      status: "Compliant",
      date: "23 Aug 2026",
    },
    {
      product: "Herbal Shampoo",
      manufacturer: "Nature Care",
      score: 72,
      status: "Violation",
      date: "23 Aug 2026",
    },
    {
      product: "Packaged Rice",
      manufacturer: "Sri Foods",
      score: 88,
      status: "Compliant",
      date: "22 Aug 2026",
    },
    {
      product: "Fruit Juice",
      manufacturer: "FreshLife",
      score: 61,
      status: "Violation",
      date: "22 Aug 2026",
    },
  ];

  function handleMenuClick(name) {
    setActive(name);

    if (name === "Scan Product") {
      setResult(false);
      setSelectedImage(null);
      setAnalyzing(false);
    }
  }

  function handleImage(event) {
    const file = event.target.files[0];

    if (!file) return;

    const imageURL = URL.createObjectURL(file);
    setSelectedImage(imageURL);
    setResult(false);
  }

  function startAnalysis() {
    if (!selectedImage) return;

    setAnalyzing(true);

    setTimeout(() => {
      setAnalyzing(false);
      setResult(true);
    }, 3000);
  }

  function resetScan() {
    setSelectedImage(null);
    setResult(false);
    setAnalyzing(false);
  }
  if (!loggedIn) {
  return <LoginPage onLogin={() => setLoggedIn(true)} />;
}
 
  return (
    <div className="min-h-screen bg-[#07111f] text-white">

      {/* SIDEBAR */}
      <aside className="fixed left-0 top-0 z-30 hidden h-screen w-64 border-r border-white/10 bg-[#0a1627] lg:block">

        <div className="flex h-20 items-center gap-3 border-b border-white/10 px-6">

          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-400 text-[#07111f] shadow-lg shadow-cyan-400/20">
            <ShieldCheck size={24} />
          </div>

          <div>
            <h1 className="text-lg font-bold">MetroCheck</h1>
            <p className="text-xs text-cyan-300">AI Compliance</p>
          </div>

        </div>

        <div className="px-4 py-6">

          <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-widest text-slate-500">
            Workspace
          </p>

          {menu.map((item) => {

            const Icon = item.icon;
            const selected = active === item.name;

            return (
              <button
                key={item.name}
                onClick={() => handleMenuClick(item.name)}
                className={`mb-2 flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm transition ${
                  selected
                    ? "bg-cyan-400/10 text-cyan-300 ring-1 ring-cyan-400/20"
                    : "text-slate-400 hover:bg-white/5 hover:text-white"
                }`}
              >

                <Icon size={19} />

                {item.name}

                {selected && (
                  <ChevronRight size={16} className="ml-auto" />
                )}

              </button>
            );
          })}

        </div>

        <div className="absolute bottom-5 left-4 right-4 rounded-2xl border border-cyan-400/10 bg-cyan-400/5 p-4">

          <div className="mb-2 flex items-center gap-2">
            <Sparkles size={16} className="text-cyan-300" />
            <span className="text-sm font-semibold">
              AI Inspector
            </span>
          </div>

          <p className="text-xs leading-5 text-slate-400">
            Automated product compliance powered by AI.
          </p>

        </div>

      </aside>

      {/* MAIN */}
      <main className="lg:ml-64">

        {/* HEADER */}
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-white/10 bg-[#07111f]/90 px-5 backdrop-blur-xl lg:px-8">

          <div className="flex items-center gap-3">

            <button className="rounded-lg p-2 hover:bg-white/5 lg:hidden">
              <Menu size={22} />
            </button>

            <div>
              <p className="text-xs text-slate-500">
                LEGAL METROLOGY
              </p>

              <h2 className="font-semibold">
                {active}
              </h2>
            </div>

          </div>

          <div className="flex items-center gap-4">

            <button className="hidden rounded-xl border border-white/10 bg-white/5 p-2.5 text-slate-300 sm:block">
              <Search size={18} />
            </button>

            <button className="relative rounded-xl border border-white/10 bg-white/5 p-2.5 text-slate-300">
              <Bell size={18} />

              <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-cyan-400" />
            </button>

            <div className="flex items-center gap-3 border-l border-white/10 pl-4">

              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 font-bold text-[#07111f]">
                I
              </div>

              <div className="hidden sm:block">
                <p className="text-sm font-medium">
                  Inspector
                </p>

                <p className="text-xs text-slate-500">
                  Authorized User
                </p>
              </div>

            </div>

          </div>

        </header>


        {/* CONTENT */}

        <div className="p-5 lg:p-8">

          {active === "Dashboard" && (
            <Dashboard
              inspections={inspections}
              onScan={() => handleMenuClick("Scan Product")}
            />
          )}


          {active === "Scan Product" && (

            <ScanPage
              selectedImage={selectedImage}
              analyzing={analyzing}
              result={result}
              handleImage={handleImage}
              startAnalysis={startAnalysis}
              resetScan={resetScan}
            />

          )}
          {active === "Inspection History" && <HistoryPage />}

          {active === "Reports" && <ReportsPage />}

          {active === "Settings" && <SettingsPage />}

                  </div>
                </main>
              </div>
            );
          }


/* ================= DASHBOARD ================= */

function Dashboard({ inspections, onScan }) {

  return (

    <>

      {/* HERO */}

      <section className="relative mb-7 overflow-hidden rounded-3xl border border-cyan-400/10 bg-gradient-to-br from-cyan-500/10 via-blue-500/5 to-transparent p-7 lg:p-9">

        <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-cyan-400/10 blur-3xl" />

        <div className="relative max-w-3xl">

          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1.5 text-xs text-cyan-300">

            <Sparkles size={13} />

            AI-POWERED INSPECTION

          </div>

          <h1 className="text-3xl font-bold leading-tight lg:text-4xl">

            Smart Product

            <span className="text-cyan-300">
              {" "}Compliance{" "}
            </span>

            Inspection

          </h1>

          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 lg:text-base">

            Automatically analyze packaged commodities, verify mandatory
            declarations and identify potential Legal Metrology violations.

          </p>

          <button
            onClick={onScan}
            className="mt-6 flex items-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-[#07111f] shadow-lg shadow-cyan-400/20 transition hover:-translate-y-0.5 hover:bg-cyan-300"
          >

            <ScanLine size={19} />

            Scan New Product

          </button>

        </div>

      </section>


      {/* STATS */}

      <section className="mb-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <StatCard
          icon={<Package />}
          title="Total Inspections"
          value="1,284"
          change="+12.8%"
          color="cyan"
        />

        <StatCard
          icon={<CheckCircle2 />}
          title="Compliant"
          value="1,041"
          change="+8.4%"
          color="green"
        />

        <StatCard
          icon={<AlertTriangle />}
          title="Violations"
          value="243"
          change="+4.2%"
          color="orange"
        />

        <StatCard
          icon={<Clock3 />}
          title="Pending Review"
          value="18"
          change="Today"
          color="purple"
        />

      </section>


      {/* QUICK ANALYSIS */}

      <section className="mb-7 grid gap-5 xl:grid-cols-3">

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 xl:col-span-2">

          <div className="mb-5 flex items-center justify-between">

            <div>

              <h3 className="font-semibold">
                Quick Product Analysis
              </h3>

              <p className="mt-1 text-xs text-slate-500">
                Upload a package image to begin AI inspection
              </p>

            </div>

            <ScanLine className="text-cyan-300" size={22} />

          </div>

          <button
            onClick={onScan}
            className="group w-full cursor-pointer rounded-2xl border border-dashed border-slate-600 bg-[#091524] p-10 text-center transition hover:border-cyan-400/50 hover:bg-cyan-400/[0.03]"
          >

            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-300">

              <Upload size={25} />

            </div>

            <h4 className="mt-4 font-medium">
              Drop product image here
            </h4>

            <p className="mt-1 text-xs text-slate-500">
              PNG, JPG or WEBP • Maximum 10 MB
            </p>

            <span className="mt-5 inline-block rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm">
              Open Scanner
            </span>

          </button>

        </div>


        {/* SCORE */}

        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6">

          <h3 className="font-semibold">
            Compliance Overview
          </h3>

          <p className="mt-1 text-xs text-slate-500">
            Current inspection statistics
          </p>

          <div className="flex items-center justify-center py-5">

            <div className="relative flex h-40 w-40 items-center justify-center rounded-full border-[12px] border-cyan-400/20">

              <div className="absolute inset-0 rounded-full border-[12px] border-transparent border-t-cyan-400 border-r-cyan-400 rotate-12" />

              <div className="text-center">

                <p className="text-3xl font-bold">
                  81%
                </p>

                <p className="text-xs text-slate-500">
                  Overall Score
                </p>

              </div>

            </div>

          </div>

          <Progress label="Declarations" value="92%" />
          <Progress label="MRP Validation" value="87%" />
          <Progress label="Quantity" value="96%" />

        </div>

      </section>


      {/* TABLE */}

      <section className="rounded-2xl border border-white/10 bg-white/[0.03]">

        <div className="flex items-center justify-between border-b border-white/10 p-6">

          <div>

            <h3 className="font-semibold">
              Recent Inspections
            </h3>

            <p className="mt-1 text-xs text-slate-500">
              Latest product compliance checks
            </p>

          </div>

          <button className="text-xs text-cyan-300">
            View All →
          </button>

        </div>

        <div className="overflow-x-auto">

          <table className="w-full min-w-[700px] text-left text-sm">

            <thead>

              <tr className="border-b border-white/5 text-xs text-slate-500">

                <th className="px-6 py-4">PRODUCT</th>
                <th className="px-6 py-4">MANUFACTURER</th>
                <th className="px-6 py-4">SCORE</th>
                <th className="px-6 py-4">STATUS</th>
                <th className="px-6 py-4">DATE</th>

              </tr>

            </thead>

            <tbody>

              {inspections.map((item) => (

                <tr
                  key={item.product}
                  className="border-b border-white/5 hover:bg-white/[0.02]"
                >

                  <td className="px-6 py-4 font-medium">
                    {item.product}
                  </td>

                  <td className="px-6 py-4 text-slate-400">
                    {item.manufacturer}
                  </td>

                  <td className="px-6 py-4 font-semibold text-cyan-300">
                    {item.score}%
                  </td>

                  <td className="px-6 py-4">

                    <span
                      className={`rounded-full px-3 py-1 text-xs ${
                        item.status === "Compliant"
                          ? "bg-emerald-400/10 text-emerald-300"
                          : "bg-orange-400/10 text-orange-300"
                      }`}
                    >

                      {item.status}

                    </span>

                  </td>

                  <td className="px-6 py-4 text-slate-500">
                    {item.date}
                  </td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </section>

    </>

  );
}


/* ================= SCAN PAGE ================= */

function ScanPage({
  selectedImage,
  analyzing,
  result,
  handleImage,
  startAnalysis,
  resetScan,
}) {
  const [cameraOpen, setCameraOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const videoRef = useRef(null);

  // OPEN CAMERA
  async function openCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "environment",
        },
        audio: false,
      });

      setCameraStream(stream);
      setCameraOpen(true);

      setTimeout(() => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      }, 100);

    } catch (error) {
      console.error("Camera error:", error);

      alert(
        "Camera access was denied or your device does not have a camera."
      );
    }
  }

  // CAPTURE PHOTO
  function capturePhoto() {
    const video = videoRef.current;

    if (!video) return;

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    const image = canvas.toDataURL("image/jpeg", 0.9);

    setCapturedImage(image);

    stopCamera();
  }

  // STOP CAMERA
  function stopCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => {
        track.stop();
      });
    }

    setCameraStream(null);
    setCameraOpen(false);
  }

  // RETAKE
  function retakePhoto() {
    setCapturedImage(null);
    openCamera();
  }

  // USE PHOTO
  function useCapturedPhoto() {
    if (!capturedImage) return;

    setCameraOpen(false);
  }

  if (result) {
    return (
      <ResultPage
        selectedImage={selectedImage}
        resetScan={resetScan}
      />
    );
  }

  return (
    <div className="mx-auto max-w-5xl">

      {/* HEADER */}

      <div className="mb-7">

        <div className="mb-3 flex items-center gap-2 text-cyan-300">

          <ScanLine size={20} />

          <span className="text-sm font-medium">
            AI PRODUCT INSPECTOR
          </span>

        </div>

        <h1 className="text-3xl font-bold">
          Scan & Analyze Product
        </h1>

        <p className="mt-2 text-slate-500">
          Upload a clear image of the product package for
          automated compliance checking.
        </p>

      </div>


      {/* CAMERA */}

      {cameraOpen && (

        <div className="rounded-3xl border border-cyan-400/20 bg-white/[0.03] p-6">

          <div className="mb-5 flex items-center justify-between">

            <div>

              <h2 className="font-semibold">
                Live Camera Scanner
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Position the product clearly inside the frame.
              </p>

            </div>

            <div className="flex items-center gap-2 rounded-full bg-red-400/10 px-3 py-1.5 text-xs text-red-300">

              <span className="h-2 w-2 animate-pulse rounded-full bg-red-400" />

              LIVE

            </div>

          </div>


          <div className="relative overflow-hidden rounded-2xl bg-black">

            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="max-h-[550px] w-full object-contain"
            />

            {/* SCANNING FRAME */}

            <div className="pointer-events-none absolute inset-0 flex items-center justify-center">

              <div className="relative h-[70%] w-[70%] rounded-2xl border-2 border-cyan-400/70">

                <div className="absolute left-0 top-0 h-7 w-7 border-l-4 border-t-4 border-cyan-300" />

                <div className="absolute right-0 top-0 h-7 w-7 border-r-4 border-t-4 border-cyan-300" />

                <div className="absolute bottom-0 left-0 h-7 w-7 border-b-4 border-l-4 border-cyan-300" />

                <div className="absolute bottom-0 right-0 h-7 w-7 border-b-4 border-r-4 border-cyan-300" />

                <div className="absolute left-0 right-0 top-1/2 h-px animate-pulse bg-cyan-400/60" />

              </div>

            </div>

          </div>


          {/* CAMERA CONTROLS */}

          <div className="mt-6 flex items-center justify-center gap-4">

            <button
              onClick={stopCamera}
              className="rounded-xl border border-white/10 px-5 py-3 text-sm text-slate-400 hover:bg-white/5"
            >
              Cancel
            </button>

            <button
              onClick={capturePhoto}
              className="flex items-center gap-2 rounded-full bg-cyan-400 px-7 py-4 font-semibold text-[#07111f] shadow-lg shadow-cyan-400/20 transition hover:scale-105 hover:bg-cyan-300"
            >

              <Camera size={21} />

              Capture Photo

            </button>

          </div>

        </div>

      )}


      {/* CAPTURED PHOTO */}

      {!cameraOpen && capturedImage && !selectedImage && (

        <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-7">

          <div className="mb-5">

            <h2 className="font-semibold">
              Captured Product
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Review the image before starting AI analysis.
            </p>

          </div>


          <div className="overflow-hidden rounded-2xl border border-white/10 bg-black">

            <img
              src={capturedImage}
              alt="Captured product"
              className="max-h-[500px] w-full object-contain"
            />

          </div>


          <div className="mt-6 flex flex-col gap-3 sm:flex-row">

            <button
              onClick={retakePhoto}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm text-slate-300 hover:bg-white/5"
            >

              <RotateCcw size={17} />

              Retake

            </button>

            <button
              onClick={useCapturedPhoto}
              className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-cyan-400 px-5 py-3 font-semibold text-[#07111f] hover:bg-cyan-300"
            >

              <CheckCircle2 size={18} />

              Use This Photo

            </button>

          </div>

        </div>

      )}


      {/* UPLOAD + CAMERA OPTIONS */}

      {!selectedImage &&
        !capturedImage &&
        !cameraOpen && (

          <div className="grid gap-5 lg:grid-cols-2">

            {/* UPLOAD */}

            <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-7">

              <div className="mb-6 flex items-center gap-3">

                <div className="rounded-xl bg-cyan-400/10 p-3 text-cyan-300">

                  <Upload size={22} />

                </div>

                <div>

                  <h2 className="font-semibold">
                    Upload Product
                  </h2>

                  <p className="text-xs text-slate-500">
                    JPG, PNG or WEBP
                  </p>

                </div>

              </div>


              <label className="flex min-h-[300px] cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-600 bg-[#091524] text-center transition hover:border-cyan-400">

                <Upload
                  size={40}
                  className="mb-4 text-cyan-300"
                />

                <p className="font-medium">
                  Drop your product image here
                </p>

                <p className="mt-2 text-xs text-slate-500">
                  or click to browse files
                </p>

                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImage}
                  className="hidden"
                />

              </label>

            </div>


            {/* CAMERA */}

            <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-cyan-400/10 to-blue-500/5 p-7">

              <div className="flex min-h-[300px] flex-col items-center justify-center text-center">

                <div className="mb-5 flex h-20 w-20 items-center justify-center rounded-3xl bg-cyan-400/10 text-cyan-300">

                  <Camera size={35} />

                </div>

                <h2 className="text-xl font-semibold">
                  Scan with Camera
                </h2>

                <p className="mt-2 max-w-sm text-sm text-slate-500">
                  Use your device camera to capture the
                  product package directly.
                </p>

                <button
                  onClick={openCamera}
                  className="mt-6 flex items-center gap-2 rounded-xl bg-cyan-400/10 px-5 py-3 text-sm text-cyan-300 transition hover:bg-cyan-400/20"
                >

                  <Camera size={18} />

                  Camera Scan

                </button>

                <p className="mt-4 text-xs text-slate-600">
                  Camera permission will be requested.
                </p>

              </div>

            </div>

          </div>

        )}


      {/* ANALYSIS PREVIEW */}

      {selectedImage &&
        !analyzing && (

          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-7">

            <div className="grid gap-7 lg:grid-cols-2">

              <div>

                <p className="mb-3 text-sm text-slate-400">
                  Uploaded Product
                </p>

                <div className="overflow-hidden rounded-2xl border border-white/10 bg-black">

                  <img
                    src={selectedImage}
                    alt="Product"
                    className="max-h-[450px] w-full object-contain"
                  />

                </div>

              </div>


              <div className="flex flex-col justify-center">

                <div className="mb-5 rounded-2xl border border-cyan-400/10 bg-cyan-400/5 p-5">

                  <div className="flex items-center gap-3">

                    <Sparkles className="text-cyan-300" />

                    <div>

                      <p className="font-semibold">
                        Ready for AI Analysis
                      </p>

                      <p className="text-xs text-slate-500">
                        OCR + NLP + Rule Engine
                      </p>

                    </div>

                  </div>

                </div>


                <button
                  onClick={startAnalysis}
                  className="flex items-center justify-center gap-2 rounded-xl bg-cyan-400 px-5 py-4 font-semibold text-[#07111f] shadow-lg shadow-cyan-400/20 hover:bg-cyan-300"
                >

                  <ScanLine size={20} />

                  Analyze Product

                </button>


                <button
                  onClick={resetScan}
                  className="mt-3 flex items-center justify-center gap-2 rounded-xl border border-white/10 px-5 py-3 text-sm text-slate-400 hover:bg-white/5"
                >

                  <RotateCcw size={16} />

                  Choose Different Image

                </button>

              </div>

            </div>

          </div>

        )}


      {/* ANALYZING */}

      {analyzing && (

        <div className="rounded-3xl border border-cyan-400/10 bg-white/[0.03] p-10 text-center">

          <div className="mx-auto mb-6 flex h-20 w-20 animate-pulse items-center justify-center rounded-3xl bg-cyan-400/10">

            <Sparkles
              size={35}
              className="text-cyan-300"
            />

          </div>

          <h2 className="text-2xl font-bold">
            AI is analyzing the product...
          </h2>

          <p className="mt-2 text-slate-500">
            Please wait while MetroCheck processes the package.
          </p>


          <div className="mx-auto mt-8 max-w-md space-y-4 text-left">

            <ProcessingStep text="Image preprocessing" />

            <ProcessingStep text="OCR text extraction" />

            <ProcessingStep text="Information extraction" />

            <ProcessingStep text="Legal rule validation" />

            <ProcessingStep text="Generating compliance report" />

          </div>

        </div>

      )}

    </div>
  );
}


/* ================= RESULT ================= */

function ResultPage({ selectedImage, resetScan }) {
  const requirements = [
    ["Product Name", true, "ABC Biscuits", "98%"],
    ["Manufacturer Details", true, "ABC Foods Pvt Ltd", "96%"],
    ["Net Quantity", true, "200 g", "99%"],
    ["Maximum Retail Price", true, "₹50", "97%"],
    ["Packing / Manufacturing Date", true, "06/2026", "94%"],
    ["Consumer Care Details", false, "Not detected", "—"],
  ];

  return (
    <div className="mx-auto max-w-7xl">

      {/* HEADER */}
      <div className="mb-7 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">

        <div>
          <div className="mb-2 flex items-center gap-2 text-cyan-300">
            <FileCheck2 size={19} />
            <span className="text-sm font-medium">
              INSPECTION COMPLETE
            </span>
          </div>

          <h1 className="text-3xl font-bold lg:text-4xl">
            Compliance Result
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            AI-powered analysis of the uploaded product package
          </p>
        </div>

        <button
          onClick={resetScan}
          className="flex items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm text-slate-300 transition hover:bg-white/5"
        >
          <ScanLine size={17} />
          New Inspection
        </button>

      </div>


      {/* TOP RESULT */}
      <div className="grid gap-5 xl:grid-cols-3">

        {/* IMAGE */}
        <div className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.03] xl:col-span-2">

          <div className="flex items-center justify-between border-b border-white/10 px-6 py-4">

            <div>
              <h3 className="font-semibold">
                AI Evidence Map
              </h3>

              <p className="mt-1 text-xs text-slate-500">
                Product image analyzed by MetroCheck AI
              </p>
            </div>

            <div className="flex items-center gap-2 rounded-full bg-cyan-400/10 px-3 py-1.5 text-xs text-cyan-300">
              <Sparkles size={13} />
              AI Verified
            </div>

          </div>


          <div className="relative flex min-h-[430px] items-center justify-center bg-[#050c16] p-6">

            {selectedImage && (
              <img
                src={selectedImage}
                alt="Scanned product"
                className="max-h-[430px] max-w-full rounded-xl object-contain"
              />
            )}

            {/* AI LABELS */}
            <div className="absolute left-[15%] top-[18%] hidden rounded-lg border border-cyan-400/70 bg-[#07111f]/90 px-3 py-2 text-xs text-cyan-300 shadow-lg shadow-cyan-400/10 md:block">
              ✓ Product detected
            </div>

            <div className="absolute right-[12%] top-[32%] hidden rounded-lg border border-emerald-400/70 bg-[#07111f]/90 px-3 py-2 text-xs text-emerald-300 md:block">
              ✓ MRP detected
            </div>

            <div className="absolute bottom-[18%] left-[18%] hidden rounded-lg border border-emerald-400/70 bg-[#07111f]/90 px-3 py-2 text-xs text-emerald-300 md:block">
              ✓ Net quantity
            </div>

            <div className="absolute bottom-[20%] right-[10%] hidden rounded-lg border border-red-400/70 bg-[#07111f]/90 px-3 py-2 text-xs text-red-300 md:block">
              ✕ Missing declaration
            </div>

          </div>


          {/* IMAGE FOOTER */}
          <div className="grid grid-cols-3 border-t border-white/10">

            <div className="p-4 text-center">

              <p className="text-lg font-bold text-cyan-300">
                98%
              </p>

              <p className="text-xs text-slate-500">
                OCR Confidence
              </p>

            </div>

            <div className="border-x border-white/10 p-4 text-center">

              <p className="text-lg font-bold text-emerald-300">
                5
              </p>

              <p className="text-xs text-slate-500">
                Fields Detected
              </p>

            </div>

            <div className="p-4 text-center">

              <p className="text-lg font-bold text-red-300">
                1
              </p>

              <p className="text-xs text-slate-500">
                Violation
              </p>

            </div>

          </div>

        </div>


        {/* RESULT CARD */}
        <div className="flex flex-col rounded-3xl border border-red-400/20 bg-gradient-to-br from-red-400/10 via-orange-400/5 to-transparent p-7">

          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-400/10 text-red-300">
            <AlertTriangle size={28} />
          </div>

          <p className="mt-6 text-sm font-medium text-red-300">
            OVERALL RESULT
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            NON-COMPLIANT
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            One mandatory declaration could not be verified.
          </p>


          {/* SCORE */}
          <div className="mt-8 rounded-2xl border border-white/10 bg-black/10 p-5">

            <div className="flex items-end justify-between">

              <div>
                <p className="text-xs text-slate-500">
                  Compliance Score
                </p>

                <p className="mt-1 text-4xl font-bold text-orange-300">
                  83%
                </p>
              </div>

              <ShieldCheck
                size={30}
                className="text-orange-300"
              />

            </div>

            <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/10">

              <div
                className="h-full rounded-full bg-orange-400"
                style={{ width: "83%" }}
              />

            </div>

          </div>


          {/* VIOLATION */}
          <div className="mt-5 rounded-2xl border border-red-400/20 bg-red-400/5 p-4">

            <div className="flex gap-3">

              <XCircle
                size={20}
                className="mt-0.5 shrink-0 text-red-300"
              />

              <div>

                <p className="text-sm font-medium text-red-200">
                  Consumer-care declaration missing
                </p>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  No consumer-care information was detected
                  in the uploaded package label.
                </p>

              </div>

            </div>

          </div>


          <button className="mt-auto flex items-center justify-center gap-2 rounded-xl bg-cyan-400 py-3.5 font-semibold text-[#07111f] transition hover:bg-cyan-300">

            <Download size={18} />

            Generate Compliance Report

          </button>

        </div>

      </div>


      {/* INFORMATION EXTRACTION */}
      <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <div className="mb-5 flex items-center justify-between">

          <div>

            <div className="flex items-center gap-3">

              <FileCheck2 className="text-cyan-300" />

              <h3 className="font-semibold">
                Extracted Product Information
              </h3>

            </div>

            <p className="mt-1 text-xs text-slate-500">
              Information identified from the package using OCR + AI
            </p>

          </div>

          <span className="hidden rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-300 sm:block">
            5 / 6 Fields Verified
          </span>

        </div>


        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">

          {requirements.map(([name, pass, value, confidence]) => (

            <div
              key={name}
              className={`rounded-2xl border p-4 ${
                pass
                  ? "border-white/5 bg-[#091524]"
                  : "border-red-400/20 bg-red-400/5"
              }`}
            >

              <div className="flex items-center justify-between">

                <div className="flex items-center gap-2">

                  {pass ? (
                    <CheckCircle2
                      size={17}
                      className="text-emerald-300"
                    />
                  ) : (
                    <XCircle
                      size={17}
                      className="text-red-300"
                    />
                  )}

                  <span className="text-xs text-slate-400">
                    {name}
                  </span>

                </div>

                <span className="text-[10px] text-slate-600">
                  {confidence}
                </span>

              </div>

              <p
                className={`mt-3 font-medium ${
                  pass
                    ? "text-white"
                    : "text-red-300"
                }`}
              >
                {value}
              </p>

            </div>

          ))}

        </div>

      </div>


      {/* RULE VALIDATION */}
      <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <div className="mb-5">

          <div className="flex items-center gap-3">

            <ShieldCheck className="text-cyan-300" />

            <h3 className="font-semibold">
              Legal Metrology Rule Validation
            </h3>

          </div>

          <p className="mt-1 text-xs text-slate-500">
            Mandatory declaration checks performed by the compliance engine
          </p>

        </div>


        <div className="overflow-hidden rounded-2xl border border-white/5">

          {requirements.map(([name, pass, value]) => (

            <div
              key={name}
              className="flex items-center justify-between border-b border-white/5 bg-[#091524] px-5 py-4 last:border-b-0"
            >

              <div className="flex items-center gap-3">

                {pass ? (
                  <CheckCircle2
                    size={19}
                    className="text-emerald-300"
                  />
                ) : (
                  <XCircle
                    size={19}
                    className="text-red-300"
                  />
                )}

                <span className="text-sm">
                  {name}
                </span>

              </div>

              <span
                className={`text-xs font-medium ${
                  pass
                    ? "text-emerald-300"
                    : "text-red-300"
                }`}
              >
                {pass ? "PASS" : "VIOLATION"}
              </span>

            </div>

          ))}

        </div>

      </div>


      {/* AI EXPLANATION */}
      <div className="mt-5 grid gap-5 lg:grid-cols-2">

        <div className="rounded-3xl border border-red-400/20 bg-red-400/5 p-6">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-red-400/10 p-3 text-red-300">
              <AlertTriangle size={21} />
            </div>

            <div>

              <h3 className="font-semibold">
                AI Violation Explanation
              </h3>

              <p className="text-xs text-slate-500">
                Why this product was flagged
              </p>

            </div>

          </div>


          <h4 className="mt-6 font-medium text-red-200">
            Consumer-care declaration is missing
          </h4>

          <p className="mt-3 text-sm leading-6 text-slate-400">
            MetroCheck AI analyzed the package label and could
            not identify a valid consumer-care declaration.
            This field should be present according to the
            applicable packaged commodity requirements.
          </p>

        </div>


        <div className="rounded-3xl border border-cyan-400/10 bg-cyan-400/5 p-6">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-cyan-400/10 p-3 text-cyan-300">
              <Info size={21} />
            </div>

            <div>

              <h3 className="font-semibold">
                Recommended Action
              </h3>

              <p className="text-xs text-slate-500">
                Suggested corrective action
              </p>

            </div>

          </div>


          <p className="mt-6 text-sm leading-6 text-slate-400">
            Add the required consumer-care information to
            the package label and re-run the inspection to
            verify compliance.
          </p>


          <button className="mt-5 flex items-center gap-2 rounded-xl border border-cyan-400/20 bg-cyan-400/10 px-4 py-2.5 text-sm text-cyan-300 hover:bg-cyan-400/20">

            <RotateCcw size={16} />

            Re-check Product

          </button>

        </div>

      </div>


      {/* PIPELINE */}
      <div className="mt-5 rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <div className="mb-5">

          <h3 className="font-semibold">
            AI Inspection Pipeline
          </h3>

          <p className="mt-1 text-xs text-slate-500">
            Processing stages completed for this inspection
          </p>

        </div>


        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">

          <Pipeline icon="01" text="Image Processing" />
          <Pipeline icon="02" text="OCR Extraction" />
          <Pipeline icon="03" text="Information Extraction" />
          <Pipeline icon="04" text="Rule Validation" />
          <Pipeline icon="05" text="AI Explanation" />

        </div>

      </div>

    </div>
  );
}


/* ================= SMALL COMPONENTS ================= */

function ProcessingStep({ text }) {

  return (

    <div className="flex items-center gap-3 rounded-xl border border-white/5 bg-[#091524] p-3">

      <div className="h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-400" />

      <span className="text-sm text-slate-300">
        {text}
      </span>

      <span className="ml-auto text-xs text-cyan-300">
        Processing
      </span>

    </div>

  );

}


function Pipeline({ icon, text }) {

  return (

    <div className="flex items-center gap-3 rounded-xl border border-emerald-400/10 bg-emerald-400/5 p-4">

      <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-400/10 text-xs text-emerald-300">

        {icon}

      </div>

      <span className="text-xs text-slate-300">
        {text}
      </span>

      <CheckCircle2
        size={15}
        className="ml-auto text-emerald-300"
      />

    </div>

  );

}


function StatCard({ icon, title, value, change, color }) {

  const colors = {
    cyan: "text-cyan-300 bg-cyan-400/10",
    green: "text-emerald-300 bg-emerald-400/10",
    orange: "text-orange-300 bg-orange-400/10",
    purple: "text-purple-300 bg-purple-400/10",
  };

  return (

    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:-translate-y-1">

      <div className="flex items-center justify-between">

        <div className={`rounded-xl p-3 ${colors[color]}`}>
          {icon}
        </div>

        <span className="text-xs text-emerald-300">
          {change}
        </span>

      </div>

      <p className="mt-5 text-xs text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-2xl font-bold">
        {value}
      </p>

    </div>

  );

}


function Progress({ label, value }) {

  return (

    <div className="mb-4">

      <div className="mb-1 flex justify-between text-xs">

        <span className="text-slate-400">
          {label}
        </span>

        <span>
          {value}
        </span>

      </div>

      <div className="h-1.5 overflow-hidden rounded-full bg-white/5">

        <div
          className="h-full rounded-full bg-cyan-400"
          style={{ width: value }}
        />

      </div>

    </div>

  );

}
function LoginPage({ onLogin }) {
  const [showPassword, setShowPassword] = useState(false);

  return (
    <div className="min-h-screen bg-[#050c16] text-white">

      <div className="grid min-h-screen lg:grid-cols-2">

        {/* LEFT SIDE */}
        <div className="relative hidden overflow-hidden lg:flex lg:flex-col lg:justify-between bg-gradient-to-br from-cyan-500/10 via-[#07111f] to-blue-500/10 p-12">

          {/* Background glow */}
          <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-cyan-400/10 blur-3xl" />

          <div className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-blue-500/10 blur-3xl" />

          {/* Logo */}
          <div className="relative flex items-center gap-3">

            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-400 text-[#07111f] shadow-lg shadow-cyan-400/20">

              <ShieldCheck size={27} />

            </div>

            <div>

              <h1 className="text-xl font-bold">
                MetroCheck
              </h1>

              <p className="text-xs text-cyan-300">
                AI Compliance Platform
              </p>

            </div>

          </div>


          {/* Main message */}
          <div className="relative max-w-xl">

            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-4 py-2 text-xs text-cyan-300">

              <Sparkles size={14} />

              AI-POWERED LEGAL METROLOGY

            </div>

            <h2 className="text-5xl font-bold leading-tight">

              Smarter

              <span className="text-cyan-300">
                {" "}Compliance.
              </span>

              <br />

              Faster Inspections.

            </h2>

            <p className="mt-6 max-w-lg text-sm leading-7 text-slate-400">

              Analyze packaged commodities using AI-powered OCR,
              information extraction and automated Legal Metrology
              rule validation.

            </p>


            {/* Feature cards */}
            <div className="mt-8 grid grid-cols-3 gap-3">

              <LoginFeature
                icon={<ScanLine size={18} />}
                text="AI Scanning"
              />

              <LoginFeature
                icon={<ShieldCheck size={18} />}
                text="Rule Validation"
              />

              <LoginFeature
                icon={<FileCheck2 size={18} />}
                text="Smart Reports"
              />

            </div>

          </div>


          <p className="relative text-xs text-slate-600">
            SIH 2026 • AI Legal Metrology Compliance
          </p>

        </div>


        {/* RIGHT SIDE */}
        <div className="flex items-center justify-center px-5 py-10">

          <div className="w-full max-w-md">

            {/* Mobile logo */}
            <div className="mb-10 flex items-center gap-3 lg:hidden">

              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400 text-[#07111f]">

                <ShieldCheck size={24} />

              </div>

              <div>

                <h1 className="font-bold">
                  MetroCheck
                </h1>

                <p className="text-xs text-cyan-300">
                  AI Compliance
                </p>

              </div>

            </div>


            <div className="mb-8">

              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-cyan-400/10 text-cyan-300">

                <ShieldCheck size={25} />

              </div>

              <h2 className="text-3xl font-bold">
                Welcome back
              </h2>

              <p className="mt-2 text-sm text-slate-500">
                Sign in to your inspection workspace.
              </p>

            </div>


            {/* FORM */}
            <div className="space-y-5">

              {/* Email */}
              <div>

                <label className="mb-2 block text-sm font-medium text-slate-300">
                  Email Address
                </label>

                <input
                  type="email"
                  placeholder="inspector@example.com"
                  className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 text-sm outline-none transition placeholder:text-slate-600 focus:border-cyan-400/50 focus:bg-cyan-400/[0.03] focus:ring-2 focus:ring-cyan-400/10"
                />

              </div>


              {/* Password */}
              <div>

                <div className="mb-2 flex items-center justify-between">

                  <label className="text-sm font-medium text-slate-300">
                    Password
                  </label>

                  <button className="text-xs text-cyan-300 hover:text-cyan-200">
                    Forgot password?
                  </button>

                </div>

                <div className="relative">

                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    className="w-full rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3.5 pr-12 text-sm outline-none transition placeholder:text-slate-600 focus:border-cyan-400/50 focus:bg-cyan-400/[0.03] focus:ring-2 focus:ring-cyan-400/10"
                  />

                  <button
                    type="button"
                    onClick={() =>
                      setShowPassword(!showPassword)
                    }
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
                  >

                    {showPassword ? "Hide" : "Show"}

                  </button>

                </div>

              </div>


              {/* Remember */}
              <div className="flex items-center gap-2">

                <input
                  type="checkbox"
                  className="h-4 w-4 accent-cyan-400"
                />

                <span className="text-xs text-slate-500">
                  Remember me
                </span>

              </div>


              {/* LOGIN */}
              <button
                onClick={onLogin}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 py-3.5 font-semibold text-[#07111f] shadow-lg shadow-cyan-400/20 transition hover:-translate-y-0.5 hover:bg-cyan-300"
              >

                Sign In

                <ChevronRight size={18} />

              </button>

            </div>


            {/* Demo info */}
            <div className="mt-8 rounded-2xl border border-cyan-400/10 bg-cyan-400/5 p-4">

              <div className="flex gap-3">

                <Info
                  size={18}
                  className="mt-0.5 shrink-0 text-cyan-300"
                />

                <div>

                  <p className="text-xs font-medium text-cyan-200">
                    Prototype Access
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Authentication will be connected to the
                    secure backend during integration.
                  </p>

                </div>

              </div>

            </div>


            <p className="mt-8 text-center text-xs text-slate-600">
              © 2026 MetroCheck AI • SIH Prototype
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}


function LoginFeature({ icon, text }) {
  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">

      <div className="mb-2 text-cyan-300">
        {icon}
      </div>

      <p className="text-xs text-slate-400">
        {text}
      </p>

    </div>
  );
}

function HistoryPage() {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");

  const inspections = [
    {
      id: "INS-1284",
      product: "Premium Biscuits",
      manufacturer: "ABC Foods Pvt Ltd",
      score: 96,
      status: "Compliant",
      date: "23 Aug 2026",
    },
    {
      id: "INS-1283",
      product: "Herbal Shampoo",
      manufacturer: "Nature Care",
      score: 72,
      status: "Violation",
      date: "23 Aug 2026",
    },
    {
      id: "INS-1282",
      product: "Packaged Rice",
      manufacturer: "Sri Foods",
      score: 88,
      status: "Compliant",
      date: "22 Aug 2026",
    },
    {
      id: "INS-1281",
      product: "Fruit Juice",
      manufacturer: "FreshLife",
      score: 61,
      status: "Violation",
      date: "22 Aug 2026",
    },
    {
      id: "INS-1280",
      product: "Organic Honey",
      manufacturer: "Nature Harvest",
      score: 94,
      status: "Compliant",
      date: "21 Aug 2026",
    },
    {
      id: "INS-1279",
      product: "Instant Noodles",
      manufacturer: "FoodWorks",
      score: 68,
      status: "Violation",
      date: "21 Aug 2026",
    },
  ];

  const filtered = inspections.filter((item) => {
    const matchesSearch =
      item.product.toLowerCase().includes(search.toLowerCase()) ||
      item.manufacturer.toLowerCase().includes(search.toLowerCase()) ||
      item.id.toLowerCase().includes(search.toLowerCase());

    const matchesFilter =
      filter === "All" || item.status === filter;

    return matchesSearch && matchesFilter;
  });

  return (
    <div className="mx-auto max-w-7xl">

      {/* HEADER */}

      <div className="mb-7">

        <div className="mb-2 flex items-center gap-2 text-cyan-300">

          <History size={19} />

          <span className="text-sm font-medium">
            INSPECTION RECORDS
          </span>

        </div>

        <h1 className="text-3xl font-bold">
          Inspection History
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Review and track previous product compliance inspections.
        </p>

      </div>


      {/* STATISTICS */}

      <div className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

        <HistoryStat
          title="Total Inspections"
          value="1,284"
          icon={<Package size={20} />}
          type="cyan"
        />

        <HistoryStat
          title="Compliant"
          value="1,041"
          icon={<CheckCircle2 size={20} />}
          type="green"
        />

        <HistoryStat
          title="Violations"
          value="243"
          icon={<AlertTriangle size={20} />}
          type="red"
        />

        <HistoryStat
          title="Avg. Score"
          value="81%"
          icon={<ShieldCheck size={20} />}
          type="purple"
        />

      </div>


      {/* TABLE CARD */}

      <div className="rounded-3xl border border-white/10 bg-white/[0.03]">

        {/* SEARCH */}

        <div className="flex flex-col gap-4 border-b border-white/10 p-5 lg:flex-row lg:items-center lg:justify-between">

          <div className="relative w-full lg:max-w-md">

            <Search
              size={18}
              className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
            />

            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search product, manufacturer or ID..."
              className="w-full rounded-xl border border-white/10 bg-[#091524] py-3 pl-11 pr-4 text-sm outline-none placeholder:text-slate-600 focus:border-cyan-400/40"
            />

          </div>


          <div className="flex gap-2">

            {["All", "Compliant", "Violation"].map((option) => (

              <button
                key={option}
                onClick={() => setFilter(option)}
                className={`rounded-xl px-4 py-2.5 text-xs transition ${
                  filter === option
                    ? "bg-cyan-400 text-[#07111f]"
                    : "border border-white/10 bg-white/5 text-slate-400 hover:bg-white/10"
                }`}
              >
                {option}
              </button>

            ))}

          </div>

        </div>


        {/* TABLE */}

        <div className="overflow-x-auto">

          <table className="w-full min-w-[850px] text-left">

            <thead>

              <tr className="border-b border-white/5 text-xs text-slate-500">

                <th className="px-6 py-4 font-medium">
                  INSPECTION ID
                </th>

                <th className="px-6 py-4 font-medium">
                  PRODUCT
                </th>

                <th className="px-6 py-4 font-medium">
                  MANUFACTURER
                </th>

                <th className="px-6 py-4 font-medium">
                  SCORE
                </th>

                <th className="px-6 py-4 font-medium">
                  STATUS
                </th>

                <th className="px-6 py-4 font-medium">
                  DATE
                </th>

                <th className="px-6 py-4 font-medium">
                  ACTION
                </th>

              </tr>

            </thead>


            <tbody>

              {filtered.map((item) => (

                <tr
                  key={item.id}
                  className="border-b border-white/5 transition hover:bg-white/[0.02]"
                >

                  <td className="px-6 py-5">

                    <span className="font-mono text-xs text-cyan-300">
                      {item.id}
                    </span>

                  </td>


                  <td className="px-6 py-5">

                    <div className="flex items-center gap-3">

                      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-400/10 text-cyan-300">

                        <Package size={17} />

                      </div>

                      <span className="text-sm font-medium">
                        {item.product}
                      </span>

                    </div>

                  </td>


                  <td className="px-6 py-5 text-sm text-slate-400">
                    {item.manufacturer}
                  </td>


                  <td className="px-6 py-5">

                    <span
                      className={`font-semibold ${
                        item.score >= 80
                          ? "text-emerald-300"
                          : "text-orange-300"
                      }`}
                    >
                      {item.score}%
                    </span>

                  </td>


                  <td className="px-6 py-5">

                    {item.status === "Compliant" ? (

                      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-300">

                        <CheckCircle2 size={13} />

                        Compliant

                      </span>

                    ) : (

                      <span className="inline-flex items-center gap-1.5 rounded-full bg-red-400/10 px-3 py-1.5 text-xs text-red-300">

                        <XCircle size={13} />

                        Violation

                      </span>

                    )}

                  </td>


                  <td className="px-6 py-5 text-xs text-slate-500">
                    {item.date}
                  </td>


                  <td className="px-6 py-5">

                    <button className="flex items-center gap-1 text-xs text-cyan-300 hover:text-cyan-200">

                      View

                      <ChevronRight size={14} />

                    </button>

                  </td>

                </tr>

              ))}

            </tbody>

          </table>


          {filtered.length === 0 && (

            <div className="py-16 text-center">

              <Search
                size={35}
                className="mx-auto mb-3 text-slate-600"
              />

              <p className="font-medium text-slate-400">
                No inspections found
              </p>

              <p className="mt-1 text-xs text-slate-600">
                Try a different search or filter.
              </p>

            </div>

          )}

        </div>


        {/* FOOTER */}

        <div className="flex items-center justify-between border-t border-white/10 px-6 py-4">

          <p className="text-xs text-slate-600">
            Showing {filtered.length} of {inspections.length} inspections
          </p>

          <div className="flex gap-2">

            <button className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-500">
              Previous
            </button>

            <button className="rounded-lg bg-cyan-400 px-3 py-2 text-xs font-medium text-[#07111f]">
              1
            </button>

            <button className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-400">
              2
            </button>

            <button className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-400">
              Next
            </button>

          </div>

        </div>

      </div>

    </div>
  );
}


function HistoryStat({ title, value, icon, type }) {

  const styles = {
    cyan: "bg-cyan-400/10 text-cyan-300",
    green: "bg-emerald-400/10 text-emerald-300",
    red: "bg-red-400/10 text-red-300",
    purple: "bg-purple-400/10 text-purple-300",
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">

      <div className="flex items-center justify-between">

        <div className={`rounded-xl p-3 ${styles[type]}`}>
          {icon}
        </div>

        <ChevronRight
          size={16}
          className="text-slate-700"
        />

      </div>

      <p className="mt-5 text-xs text-slate-500">
        {title}
      </p>

      <p className="mt-1 text-2xl font-bold">
        {value}
      </p>

    </div>
  );
}
function ReportsPage() {
  const reports = [
    {
      id: "RPT-1284",
      product: "Premium Biscuits",
      score: 96,
      status: "Compliant",
      date: "23 Aug 2026",
    },
    {
      id: "RPT-1283",
      product: "Herbal Shampoo",
      score: 72,
      status: "Violation",
      date: "23 Aug 2026",
    },
    {
      id: "RPT-1282",
      product: "Packaged Rice",
      score: 88,
      status: "Compliant",
      date: "22 Aug 2026",
    },
    {
      id: "RPT-1281",
      product: "Fruit Juice",
      score: 61,
      status: "Violation",
      date: "22 Aug 2026",
    },
  ];

  return (
    <div className="mx-auto max-w-7xl">

      <div className="mb-7">
        <div className="mb-2 flex items-center gap-2 text-cyan-300">
          <FileText size={19} />
          <span className="text-sm font-medium">
            COMPLIANCE DOCUMENTS
          </span>
        </div>

        <h1 className="text-3xl font-bold">Reports</h1>

        <p className="mt-2 text-sm text-slate-500">
          View and manage generated product compliance reports.
        </p>
      </div>

      <div className="mb-6 grid gap-4 sm:grid-cols-3">

        <HistoryStat
          title="Total Reports"
          value="1,284"
          icon={<FileText size={20} />}
          type="cyan"
        />

        <HistoryStat
          title="Compliant"
          value="1,041"
          icon={<CheckCircle2 size={20} />}
          type="green"
        />

        <HistoryStat
          title="Violations"
          value="243"
          icon={<AlertTriangle size={20} />}
          type="red"
        />

      </div>

      <div className="grid gap-4 lg:grid-cols-2">

        {reports.map((report) => (

          <div
            key={report.id}
            className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 transition hover:border-cyan-400/20"
          >

            <div className="flex items-start justify-between">

              <div className="flex items-center gap-3">

                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400/10 text-cyan-300">
                  <FileText size={21} />
                </div>

                <div>
                  <p className="font-semibold">
                    {report.product}
                  </p>

                  <p className="mt-1 font-mono text-xs text-slate-600">
                    {report.id}
                  </p>
                </div>

              </div>

              {report.status === "Compliant" ? (

                <span className="rounded-full bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-300">
                  ✓ Compliant
                </span>

              ) : (

                <span className="rounded-full bg-red-400/10 px-3 py-1.5 text-xs text-red-300">
                  ✕ Violation
                </span>

              )}

            </div>

            <div className="mt-5 grid grid-cols-3 gap-3">

              <div className="rounded-xl bg-[#091524] p-3">
                <p className="text-[10px] text-slate-600">
                  SCORE
                </p>
                <p className="mt-1 text-lg font-bold">
                  {report.score}%
                </p>
              </div>

              <div className="rounded-xl bg-[#091524] p-3">
                <p className="text-[10px] text-slate-600">
                  DATE
                </p>
                <p className="mt-1 text-xs text-slate-300">
                  {report.date}
                </p>
              </div>

              <div className="rounded-xl bg-[#091524] p-3">
                <p className="text-[10px] text-slate-600">
                  TYPE
                </p>
                <p className="mt-1 text-xs text-slate-300">
                  AI Audit
                </p>
              </div>

            </div>

            <div className="mt-5 flex gap-3">

              <button className="flex flex-1 items-center justify-center gap-2 rounded-xl border border-white/10 py-2.5 text-xs text-slate-300 hover:bg-white/5">
                <Eye size={15} />
                View Report
              </button>

              <button className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-cyan-400/10 py-2.5 text-xs text-cyan-300 hover:bg-cyan-400/20">
                <Download size={15} />
                Download
              </button>

            </div>

          </div>

        ))}

      </div>

      <div className="mt-6 rounded-2xl border border-cyan-400/10 bg-cyan-400/5 p-5">

        <div className="flex gap-3">

          <Info
            size={19}
            className="mt-0.5 shrink-0 text-cyan-300"
          />

          <div>
            <p className="text-sm font-medium text-cyan-200">
              Automated Compliance Reports
            </p>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Reports contain extracted product information,
              compliance checks, detected violations and AI-generated
              corrective recommendations.
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}

function SettingsPage() {
  const [notifications, setNotifications] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  return (
    <div className="mx-auto max-w-5xl">

      <div className="mb-7">
        <div className="mb-2 flex items-center gap-2 text-cyan-300">
          <Settings size={20} />
          <span className="text-sm font-medium">
            SYSTEM CONFIGURATION
          </span>
        </div>

        <h1 className="text-3xl font-bold">
          Settings
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Manage your MetroCheck account and inspection preferences.
        </p>
      </div>

      {/* PROFILE */}

      <div className="mb-5 rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <h2 className="text-lg font-semibold">
          Inspector Profile
        </h2>

        <p className="mt-1 text-xs text-slate-500">
          Your MetroCheck account information.
        </p>

        <div className="mt-6 flex items-center gap-5">

          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-400/10 text-xl font-bold text-cyan-300">
            IN
          </div>

          <div>
            <p className="font-semibold">
              Inspector
            </p>

            <p className="mt-1 text-sm text-slate-500">
              inspector@metrocheck.ai
            </p>

            <span className="mt-2 inline-block rounded-full bg-emerald-400/10 px-3 py-1 text-xs text-emerald-300">
              ● Active Account
            </span>
          </div>

        </div>

      </div>

      {/* ORGANIZATION */}

      <div className="mb-5 rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <h2 className="text-lg font-semibold">
          Organization
        </h2>

        <div className="mt-5 grid gap-4 md:grid-cols-2">

          <div>
            <p className="mb-2 text-xs text-slate-500">
              Organization Name
            </p>

            <div className="rounded-xl border border-white/10 bg-[#091524] px-4 py-3 text-sm text-slate-300">
              MetroCheck Inspection Unit
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs text-slate-500">
              Inspector ID
            </p>

            <div className="rounded-xl border border-white/10 bg-[#091524] px-4 py-3 text-sm text-slate-300">
              INSPECTOR-001
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs text-slate-500">
              Department
            </p>

            <div className="rounded-xl border border-white/10 bg-[#091524] px-4 py-3 text-sm text-slate-300">
              Product Compliance
            </div>
          </div>

          <div>
            <p className="mb-2 text-xs text-slate-500">
              Location
            </p>

            <div className="rounded-xl border border-white/10 bg-[#091524] px-4 py-3 text-sm text-slate-300">
              India
            </div>
          </div>

        </div>

      </div>

      {/* PREFERENCES */}

      <div className="mb-5 rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <h2 className="text-lg font-semibold">
          Inspection Preferences
        </h2>

        <div className="mt-5 space-y-3">

          <div className="flex items-center justify-between rounded-2xl bg-[#091524] p-4">

            <div>
              <p className="text-sm font-medium">
                Inspection Notifications
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Get notified when analysis is completed.
              </p>
            </div>

            <button
              onClick={() => setNotifications(!notifications)}
              className={`h-6 w-11 rounded-full p-1 transition ${
                notifications
                  ? "bg-cyan-400"
                  : "bg-slate-700"
              }`}
            >
              <div
                className={`h-4 w-4 rounded-full bg-white transition ${
                  notifications
                    ? "ml-5"
                    : "ml-0"
                }`}
              />
            </button>

          </div>


          <div className="flex items-center justify-between rounded-2xl bg-[#091524] p-4">

            <div>
              <p className="text-sm font-medium">
                Automatically Save Inspections
              </p>

              <p className="mt-1 text-xs text-slate-500">
                Save completed inspections to history.
              </p>
            </div>

            <button
              onClick={() => setAutoSave(!autoSave)}
              className={`h-6 w-11 rounded-full p-1 transition ${
                autoSave
                  ? "bg-cyan-400"
                  : "bg-slate-700"
              }`}
            >
              <div
                className={`h-4 w-4 rounded-full bg-white transition ${
                  autoSave
                    ? "ml-5"
                    : "ml-0"
                }`}
              />
            </button>

          </div>

        </div>

      </div>

      {/* SECURITY */}

      <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">

        <div className="flex items-center gap-3">

          <div className="rounded-xl bg-cyan-400/10 p-3 text-cyan-300">
            <ShieldCheck size={20} />
          </div>

          <div>
            <h2 className="font-semibold">
              Security
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Your account is protected.
            </p>
          </div>

        </div>

        <button className="mt-5 rounded-xl border border-white/10 px-4 py-3 text-sm text-slate-300 hover:bg-white/5">
          Change Password
        </button>

      </div>

    </div>
  );
}

function ToggleSetting({
  title,
  description,
  enabled,
  onChange,
}) {
  return (
    <div className="flex items-center justify-between rounded-2xl bg-[#091524] p-4">

      <div className="pr-5">

        <p className="text-sm font-medium">
          {title}
        </p>

        <p className="mt-1 text-xs text-slate-600">
          {description}
        </p>

      </div>


      <button
        onClick={onChange}
        className={`relative h-6 w-11 shrink-0 rounded-full transition ${
          enabled
            ? "bg-cyan-400"
            : "bg-slate-700"
        }`}
      >

        <span
          className={`absolute top-1 h-4 w-4 rounded-full bg-white transition ${
            enabled
              ? "left-6"
              : "left-1"
          }`}
        />

      </button>

    </div>
  );
}
export default App;