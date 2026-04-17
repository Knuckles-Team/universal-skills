# Cinematic Frontend: GSAP Patterns

When building high-fidelity landing pages in React, GSAP (GreenSock Animation Platform) is our primary tool for complex timeline orchestration and scroll-linked animations. Below are the definitive patterns for using GSAP smoothly within a React ecosystem.

## 1. The React GSAP Hook Pattern (`useGSAP`)
When working in React 18/19+, it's essential to scope your animations correctly so they clean themselves up on unmount (preventing memory leaks) and only selecting elements within your specific component instance.

Always use `@gsap/react`.

```javascript
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function HeroSection() {
  const containerRef = useRef(null);

  useGSAP(
    () => {
      // ✅ Scoped strictly to containerRef context
      // ✅ Automatically reverts when component unmounts

      const tl = gsap.timeline({
        defaults: { ease: "power3.out", duration: 1.2 }
      });

      tl.from(".hero-headline", {
        y: 60,
        opacity: 0,
        stagger: 0.1,
      })
      .from(".hero-subtext", {
        y: 20,
        opacity: 0,
      }, "-=0.8")
      .from(".cta-button", {
        scale: 0.9,
        opacity: 0,
        ease: "back.out(1.5)"
      }, "-=0.9");

    },
    { scope: containerRef } // Crucial for scoping selectors like ".hero-headline"
  );

  return (
    <section ref={containerRef} className="relative min-h-screen flex items-center">
      <h1 className="hero-headline text-6xl font-bold">Cinematic Scale.</h1>
      <h1 className="hero-headline text-6xl font-serif italic text-accent">Precision Engineering.</h1>
      <p className="hero-subtext mt-6 text-xl">The next generation.</p>
      <button className="cta-button mt-10 px-8 py-4 bg-primary rounded-full text-white">
        Start building
      </button>
    </section>
  );
}
```

## 2. Scroll-Linked "Sticky Stacking Protocol" Cards
This pattern solves the "Vertical Stacking Archive" look where scrolling down pins the section and stacks cards on top of each other.

```javascript
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export default function ProtocolArchive({ steps }) {
  const containerRef = useRef(null);
  const cardsRef = useRef([]);

  useGSAP(() => {
    // Pin the entire container
    ScrollTrigger.create({
      trigger: containerRef.current,
      start: "top top",
      end: `+=${window.innerHeight * steps.length}`,
      pin: true,
      pinSpacing: true,
    });

    // Animate each card into stack
    cardsRef.current.forEach((card, index) => {
      if (index === 0) return; // First card is already visible

      gsap.fromTo(
        card,
        {
          y: window.innerHeight,
          scale: 1,
          boxShadow: "0px 0px 0px rgba(0,0,0,0)"
        },
        {
          y: 30 * index, // Slight staggered offset
          scale: 1 - index * 0.05, // Make background cards slightly smaller
          boxShadow: "0px -20px 40px rgba(0,0,0,0.5)",
          ease: "none",
          scrollTrigger: {
            trigger: containerRef.current,
            start: `top top-=${window.innerHeight * (index - 1)}`,
            end: `top top-=${window.innerHeight * index}`,
            scrub: true,
          },
        }
      );

      // Blur the previous card as the new one covers it
      if (index > 0) {
         gsap.to(cardsRef.current[index - 1], {
           filter: "blur(10px) brightness(0.6)",
           ease: "none",
           scrollTrigger: {
             trigger: containerRef.current,
             start: `top top-=${window.innerHeight * (index - 1)}`,
             end: `top top-=${window.innerHeight * index}`,
             scrub: true,
           }
         });
      }
    });
  }, { scope: containerRef });

  return (
    <section ref={containerRef} className="relative h-screen overflow-hidden bg-black text-white">
      {steps.map((step, i) => (
        <div
          key={i}
          ref={(el) => (cardsRef.current[i] = el)}
          className="absolute inset-x-4 top-10 bottom-10 rounded-[3rem] bg-gray-900 border border-gray-800 p-12 flex flex-col justify-center"
          style={{ zIndex: i }}
        >
          <p className="font-mono text-accent mb-4">0{i + 1} // PROTOCOL</p>
          <h2 className="text-5xl font-bold mb-6">{step.title}</h2>
          <p className="text-2xl text-gray-400 max-w-2xl">{step.description}</p>
        </div>
      ))}
    </section>
  );
}
```

## 3. High-Performance Morphing Navbar
For the "Floating Island" Navbar that changes from transparent into a glassy pill shape after scrolling past the hero section.

```javascript
import { useRef, useState } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export default function GlassNavbar() {
  const navRef = useRef(null);

  useGSAP(() => {
    // Timeline to transition navbar styles
    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: "body",
        start: "top top",
        end: "100px top", // fully transitions over 100px scroll
        scrub: true,
      }
    });

    // Starting state is transparent and wider
    tl.fromTo(navRef.current, {
      backgroundColor: "rgba(255, 255, 255, 0)",
      backdropFilter: "blur(0px)",
      border: "1px solid rgba(255,255,255,0)",
      width: "100%",
      paddingTop: "24px",
      color: "white" // assuming dark background hero
    }, {
      backgroundColor: "rgba(10, 10, 15, 0.75)", // Dark glass
      backdropFilter: "blur(20px)",
      border: "1px solid rgba(255,255,255,0.1)",
      width: "80%",
      paddingTop: "16px",
      borderRadius: "9999px",
      color: "rgba(255,255,255,0.9)",
      maxWidth: "1200px"
    });
  }, []);

  return (
    <div className="fixed top-0 left-0 w-full flex justify-center z-50 pointer-events-none">
      <nav ref={navRef} className="flex justify-between items-center rounded-none px-8 pb-4 pointer-events-auto transition-all">
        <div className="font-bold text-xl tracking-tighter">BRAND</div>
        <div className="hidden md:flex space-x-8 text-sm font-medium">
          <a href="#" className="hover:text-accent transition-colors">Manifesto</a>
          <a href="#" className="hover:text-accent transition-colors">Platform</a>
          <a href="#" className="hover:text-accent transition-colors">Science</a>
        </div>
        <button className="bg-accent text-white px-5 py-2 rounded-full font-medium text-sm hover:scale-105 transition-transform">
          Access
        </button>
      </nav>
    </div>
  );
}
```
